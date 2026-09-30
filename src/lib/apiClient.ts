/**
 * Shared server-side API access.
 *
 * Every data-driven page goes through here so that an empty database, an
 * unreachable API and a slow API are three *different* outcomes. Previously the
 * catalog helpers silently substituted hardcoded sample data on any error,
 * which meant an outage published fabricated destinations, hotels and
 * testimonials. Callers now receive an explicit `ok/error` result.
 */
import { getApiBaseUrl } from "@/lib/api";

/** Generous enough for a cold MySQL/TiDB connection, short enough to fail fast. */
const DEFAULT_TIMEOUT_MS = 8000;

export type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: string; status?: number };

export class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function buildUrl(path: string): string {
  const base = getApiBaseUrl();
  return `${base}/api${path.startsWith("/") ? path : `/${path}`}`;
}

/**
 * GET a collection or object from the backend.
 *
 * `revalidate` keeps ISR behaviour that the catalog pages already relied on.
 * A thrown error is converted into `{ ok: false }` rather than being swallowed,
 * so a page can render an honest error state instead of sample records.
 */
export async function apiGet<T>(path: string, revalidate = 60): Promise<ApiResult<T>> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
  try {
    const response = await fetch(buildUrl(path), {
      signal: controller.signal,
      next: { revalidate },
    });
    if (!response.ok) {
      return {
        ok: false,
        error:
          response.status >= 500
            ? "The booking service is temporarily unavailable."
            : "We could not load this content right now.",
        status: response.status,
      };
    }
    return { ok: true, data: (await response.json()) as T };
  } catch {
    return { ok: false, error: "The booking service is currently unreachable." };
  } finally {
    clearTimeout(timer);
  }
}

/** Convenience: return the data, or `fallback` when the request failed. */
export async function apiGetOr<T>(path: string, fallback: T, revalidate = 60): Promise<T> {
  const result = await apiGet<T>(path, revalidate);
  return result.ok ? result.data : fallback;
}
