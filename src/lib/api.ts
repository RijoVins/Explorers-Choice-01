/**
 * Resolve the backend origin at runtime.
 *
 * `NEXT_PUBLIC_EXPLORERS_API_URL` is intentionally the *frontend's own* origin
 * in production: the browser then talks to `/api/*` on this same host, which
 * `next.config.ts` rewrites to the real backend. That keeps the session cookie
 * first-party, which is what makes the Google OAuth callback (a top-level
 * redirect that returns to the frontend) carry a usable session.
 *
 * Two consequences handled here:
 *
 *  1. A configured origin equal to the page's own origin is dropped in favour of
 *     a relative `/api` path. Fetching `${origin}/api/...` would be fine, but
 *     keeping it relative makes it impossible to accidentally build a
 *     self-referential URL.
 *  2. `EXPLORERS_API_URL` / `EXPLORERS_API_ORIGIN` hold the *backend* origin and
 *     are only read on the server. When `NEXT_PUBLIC_EXPLORERS_API_URL` is unset
 *     (local dev), the browser falls back to the current host's `:8000` so other
 *     devices on the LAN can reach the backend.
 */

function normalizeOrigin(value: string | undefined): string {
  const trimmed = (value ?? "").trim().replace(/\/+$/, "").replace(/\/api$/, "");
  return trimmed;
}

function isSameOrigin(candidate: string, origin: string): boolean {
  try {
    return new URL(candidate).origin === new URL(origin).origin;
  } catch {
    return false;
  }
}

export function getApiBaseUrl(): string {
  const configured = normalizeOrigin(process.env.NEXT_PUBLIC_EXPLORERS_API_URL);

  if (typeof window !== "undefined") {
    // Browser: an empty return value means "same origin", so callers produce
    // `/api/...` and the rewrite proxy handles it.
    if (!configured || isSameOrigin(configured, window.location.origin)) return "";
    return configured;
  }

  if (configured) return configured;

  const serverBackend = normalizeOrigin(process.env.EXPLORERS_API_URL ?? process.env.EXPLORERS_API_ORIGIN);
  if (serverBackend) return serverBackend;

  // Local dev fallback: LAN address of this machine on the backend's port.
  if (typeof window === "undefined" && typeof process !== "undefined") {
    return "http://127.0.0.1:8000";
  }
  return "";
}

export function buildClientApiUrl(): string {
  return `${getApiBaseUrl()}/api`;
}

/**
 * Export functions instead of constants so they're evaluated at call time, not import time.
 * This ensures Vercel's runtime environment variable is always used.
 */
export function getClientApiUrl(): string {
  return buildClientApiUrl();
}

// Backward-compatible exports for existing code
export const CLIENT_API_URL = buildClientApiUrl();
export const SERVER_API_URL = buildClientApiUrl();
