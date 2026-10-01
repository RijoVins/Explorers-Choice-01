/**
 * BUG-16: Validate image URLs against the same allowlist `next/image` uses
 * (next.config.ts remotePatterns + localhost:8000 backend). This prevents
 * editors from saving URLs that the renderer will reject.
 */

export const ALLOWED_IMAGE_HOSTS = [
  { protocol: "https", hostname: "images.unsplash.com" },
  { protocol: "https", hostname: "explorers-backend.onrender.com" },
  { protocol: "http", hostname: "localhost", port: "8000" },
  // The API base may serve images from its own host in production.
  // Keep in sync with next.config.ts remotePatterns.
];

function hostMatches(pattern: { protocol?: string; hostname: string; port?: string }, url: URL): boolean {
  if (pattern.protocol && pattern.protocol !== url.protocol.replace(":", "")) return false;
  if (url.hostname !== pattern.hostname && !url.hostname.endsWith(`.${pattern.hostname}`)) return false;
  if (pattern.port && url.port !== pattern.port) return false;
  return true;
}

/**
 * Returns true if the URL is an empty value or is allowed by next/image.
 */
export function isAllowedImageUrl(value: string, extraOrigins: string[] = []): boolean {
  const trimmed = value.trim();
  if (!trimmed) return true; // empty fields are allowed (cleared / not set)
  let url: URL;
  try {
    url = new URL(trimmed);
  } catch {
    return false;
  }
  if (url.protocol !== "http:" && url.protocol !== "https:") return false;
  if (ALLOWED_IMAGE_HOSTS.some((p) => hostMatches(p, url))) return true;
  // Also allow data: URIs and blob: since the renderer supports them.
  if (trimmed.startsWith("data:image/") || trimmed.startsWith("blob:")) return true;
  // Allow the API origin if provided (server-served uploads).
  for (const origin of extraOrigins) {
    try {
      const base = new URL(origin);
      if (base.origin === url.origin) return true;
    } catch {
      /* ignore malformed */
    }
  }
  return false;
}

/**
 * Returns an error message, or "" if the URL is acceptable.
 */
export function imageUrlError(value: string, extraOrigins: string[] = []): string {
  const trimmed = value.trim();
  if (!trimmed) return "";
  if (!isAllowedImageUrl(trimmed, extraOrigins)) {
    return "Image URLs must use a supported host (Unsplash or the site uploads service). HTTPS URLs are preferred.";
  }
  return "";
}