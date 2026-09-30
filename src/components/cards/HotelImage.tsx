"use client";

import { SafeImage } from "@/components/cards/SafeImage";

export function HotelImage({ src, name }: { src: string; name: string }) {
  return (
    <SafeImage
      src={src}
      alt={name}
      placeholder="/images/hotel-placeholder.svg"
      sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
    />
  );
}
