import Link from "next/link";
import type { Destination } from "@/lib/catalog";
import { SmartImage } from "@/components/ui/SmartImage";

export function DestinationCard({ destination }: { destination: Destination }) {
  return (
    <Link
      href={`/destinations/${destination.slug}`}
      className="group block overflow-hidden rounded-2xl border border-line bg-cream shadow-card transition-transform duration-200 hover:-translate-y-1"
    >
      <div className="relative aspect-[4/3] overflow-hidden bg-sand">
        <SmartImage
          src={destination.image}
          alt={destination.name}
          fill
          sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
          className="object-cover transition-transform duration-500 group-hover:scale-105"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-dark/40 to-transparent" />
        {destination.region ? (
          <span className="absolute left-4 top-4 rounded-full bg-ivory/90 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-forest">
            {destination.region}
          </span>
        ) : null}
      </div>
      <div className="p-6">
        <h3 className="font-display text-2xl text-forest">{destination.name}</h3>
        <p className="mt-1 text-sm uppercase tracking-wide text-terracotta">
          {destination.country}
        </p>
        <p className="mt-3 text-sm leading-relaxed text-charcoal-soft line-clamp-2">
          {destination.tagline}
        </p>
        <span className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-forest">
          Explore destination
          <svg
            className="h-4 w-4 transition-transform group-hover:translate-x-1"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </span>
      </div>
    </Link>
  );
}
