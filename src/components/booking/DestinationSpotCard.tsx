import Link from "next/link";
import { SafeImage } from "@/components/cards/SafeImage";
import type { Destination } from "@/lib/catalog";

export function DestinationSpotCard({ destination }: { destination: Destination }) {
  return (
    <Link
      href={`/book?destination=${destination.slug}`}
      className="group block overflow-hidden rounded-2xl border border-line bg-cream shadow-card transition-transform duration-200 hover:-translate-y-1"
    >
      <div className="relative aspect-[4/3] overflow-hidden bg-sand">
        <SafeImage
          src={destination.image}
          alt={destination.name}
          sizes="(min-width: 1024px) 25vw, (min-width: 640px) 33vw, 100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-dark/40 to-transparent" />
        {destination.region ? (
          <span className="absolute left-4 top-4 rounded-full bg-ivory/90 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-forest">
            {destination.region}
          </span>
        ) : null}
      </div>
      <div className="p-5">
        <h3 className="font-display text-xl text-forest">{destination.name}</h3>
        {destination.country ? (
          <p className="mt-1 text-xs uppercase tracking-wide text-terracotta">{destination.country}</p>
        ) : null}
        {destination.tagline ? (
          <p className="mt-2 text-sm leading-relaxed text-charcoal-soft line-clamp-2">{destination.tagline}</p>
        ) : null}
        <span className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-forest">
          Book this spot
          <svg
            className="h-4 w-4 transition-transform group-hover:translate-x-1"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </span>
      </div>
    </Link>
  );
}