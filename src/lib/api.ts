/**
 * Get the backend base URL at runtime (not build time).
 * This ensures Vercel's environment variable is always used, not a build-time default.
 */
export function getApiBaseUrl(): string {
  const configured = typeof process !== "undefined" && typeof process.env !== "undefined"
    ? process.env.NEXT_PUBLIC_EXPLORERS_API_URL
    : undefined;
  return (configured || "https://explorers-backend.onrender.com")
    .replace(/\/+$/, "")
    .replace(/\/api$/, "");
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
