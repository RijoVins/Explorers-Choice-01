"use client";

import Image from "next/image";
import { useState } from "react";

const GENERIC_PLACEHOLDER = "/images/image-placeholder.svg";

/**
 * `next/image` throws when `src` is an empty string, and database records can
 * legitimately have no image yet. This renders a branded placeholder instead of
 * crashing the page, and also recovers if a configured remote URL 404s.
 */
export function SafeImage({
  src,
  alt,
  placeholder = GENERIC_PLACEHOLDER,
  sizes = "(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw",
  className = "object-cover transition-transform duration-500 group-hover:scale-105",
  priority = false,
}: {
  src: string | null | undefined;
  alt: string;
  placeholder?: string;
  sizes?: string;
  className?: string;
  priority?: boolean;
}) {
  const [failedSrc, setFailedSrc] = useState<string | null>(null);
  const usePlaceholder = !src || failedSrc === src;
  const resolved = usePlaceholder ? placeholder : src;

  return (
    <Image
      src={resolved}
      alt={usePlaceholder ? `${alt} — placeholder illustration` : alt}
      fill
      sizes={sizes}
      priority={priority}
      className={className}
      onError={() => {
        if (!usePlaceholder) setFailedSrc(src);
      }}
    />
  );
}
