import type { NextConfig } from "next";

const externalApi = process.env.NEXT_PUBLIC_EXPLORERS_API_URL ? ` ${process.env.NEXT_PUBLIC_EXPLORERS_API_URL}` : "";

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
        protocol: "http",
        hostname: "localhost",
        port: "8000",
      },
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
    return [
      {
        source: "/api/:path*",
        destination: "https://api.explorerschoice.online/api/:path*",
      },
    ];
  },
};

export default nextConfig;
