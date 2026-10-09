import type { NextConfig } from "next";

/** Strip trailing slashes and any trailing `/api` so we are left with a bare origin. */
function normalizeOrigin(value: string | undefined): string {
  const trimmed = (value ?? "").trim().replace(/\/+$/, "").replace(/\/api$/, "");
  if (!trimmed) return "";
  try {
    return new URL(trimmed).origin;
  } catch {
    return "";
  }
}

/**
 * The backend origin, resolved server-side only.
 *
 * `NEXT_PUBLIC_EXPLORERS_API_URL` deliberately points at *this* site so that the
 * browser makes same-origin requests and the session cookie stays first-party.
 * It must therefore never be used as a rewrite destination — see below.
 */
function backendOrigin(): string {
  return normalizeOrigin(process.env.EXPLORERS_API_URL ?? process.env.EXPLORERS_API_ORIGIN);
}

/**
 * Origins that belong to this deployment.
 *
 * A rewrite whose destination is one of these turns `/api/x` into
 * `<self>/api/x`, which matches the very same rewrite again, on every pass.
 * Vercel detects the recursion and answers `508 INFINITE_LOOP_DETECTED` for all
 * API traffic — which is exactly what broke "Continue with Google".
 */
function selfOrigins(): string[] {
  return [
    process.env.NEXT_PUBLIC_EXPLORERS_API_URL,
    process.env.NEXT_PUBLIC_SITE_URL,
    process.env.VERCEL_PROJECT_PRODUCTION_URL
      ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`
      : "",
    process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : "",
  ]
    .map(normalizeOrigin)
    .filter(Boolean);
}

const externalApi = (() => {
  const origin = backendOrigin();
  return origin ? ` ${origin}` : "";
})();

/** Allow next/image to render media the backend itself serves. */
const backendImagePattern = (() => {
  const origin = backendOrigin();
  if (!origin) return null;
  try {
    const url = new URL(origin);
    return {
      protocol: url.protocol.replace(":", "") as "http" | "https",
      hostname: url.hostname,
      ...(url.port ? { port: url.port } : {}),
    };
  } catch {
    return null;
  }
})();

// BUG-15: src/lib/api.ts falls back to {protocol}//{hostname}:8000 when served
// over the LAN so other devices can reach the backend. In non-production builds
// we must include that LAN port in connect-src/img-src or requests are blocked
// by CSP. Production environments should always set NEXT_PUBLIC_EXPLORERS_API_URL.
const isProd = process.env.NODE_ENV === "production";
const lanApiSource = isProd
  ? ""
  : " http://127.0.0.1:8000 ws://localhost:3000 ws://127.0.0.1:3000";

const securityHeaders = [
  { key: "X-Frame-Options", value: "DENY" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "X-DNS-Prefetch-Control", value: "on" },
  {
    key: "Strict-Transport-Security",
    value: "max-age=63072000; includeSubDomains; preload",
  },
  {
    key: "Content-Security-Policy",
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
      "style-src 'self' 'unsafe-inline'",
      `img-src 'self' https://images.unsplash.com http://localhost:8000${externalApi}${lanApiSource} data: blob:`,
      "font-src 'self'",
      `connect-src 'self' http://localhost:8000${externalApi}${lanApiSource}`,
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join("; "),
  },
];

const nextConfig: NextConfig = {
  poweredByHeader: false,
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
      {
        protocol: "https",
        hostname: "explorers-backend.onrender.com",
      },
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
      },
      ...(backendImagePattern ? [backendImagePattern] : []),
    ],
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: securityHeaders,
      },
    ];
  },
  async rewrites() {
    const destination = backendOrigin();

    if (!destination) {
      // No backend configured (e.g. a pure marketing deploy). Registering the
      // rewrite anyway would send `/api/*` to a dead host.
      return [];
    }

    if (selfOrigins().includes(destination)) {
      // Fail the build loudly rather than ship a site whose entire API surface
      // answers 508 INFINITE_LOOP_DETECTED.
      throw new Error(
        `next.config: refusing to rewrite /api/* to ${destination} because that is this ` +
          `deployment's own origin, which loops. Set EXPLORERS_API_URL to the backend origin ` +
          `(e.g. https://api.explorerschoice.online).`,
      );
    }

    return [
      {
        source: "/api/:path*",
        destination: `${destination}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
