"use client";

import Image from "next/image";
import { useState } from "react";
import type { ImageProps } from "next/image";

export const FALLBACK_IMAGE =
  "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1600&q=80";

export function SmartImage(props: ImageProps) {
  const [src, setSrc] = useState<ImageProps["src"]>(props.src || FALLBACK_IMAGE);

  return (
    <Image
      {...props}
      src={src || FALLBACK_IMAGE}
      onError={() => {
        if (src !== FALLBACK_IMAGE) setSrc(FALLBACK_IMAGE);
      }}
    />
  );
}