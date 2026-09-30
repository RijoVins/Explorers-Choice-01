import Link from "next/link";
import type { CatalogPackage } from "@/lib/catalog";
import { formatMoney } from "@/lib/catalog";
import { SafeImage } from "@/components/cards/SafeImage";

export function PackageCard({ pkg }: { pkg: CatalogPackage }) {
  return (
    <article className="group flex flex-col overflow-hidden rounded-2xl border border-line bg-cream shadow-card transition-transform duration-200 hover:-translate-y-1">
      <Link href={`/packages/${pkg.slug}`} className="relative block aspect-[3/2] overflow-hidden bg-sand">
        <SafeImage
          src={pkg.image}
          alt={pkg.name}
          sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-dark/50 to-transparent" />
        {pkg.country ? (
          <span className="absolute left-4 top-4 rounded-full bg-ivory/90 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-forest">
            {pkg.country}
          </span>
        ) : null}
        {pkg.durationDays > 0 ? (
          <span className="absolute bottom-4 left-4 right-4 flex items-end justify-between">
            <span className="rounded-full bg-ivory/90 px-3 py-1 text-xs font-semibold text-forest">
              {pkg.durationDays} {pkg.durationDays === 1 ? "day" : "days"}
            </span>
          </span>
        ) : null}
      </Link>

      <div className="flex flex-1 flex-col p-6">
        <Link href={`/packages/${pkg.slug}`}>
          <h3 className="font-display text-2xl leading-snug text-forest transition-colors group-hover:text-forest-light">
            {pkg.name}
          </h3>
          {pkg.destination ? (
            <p className="mt-1 text-sm uppercase tracking-wide text-terracotta">{pkg.destination}</p>
          ) : null}
        </Link>

        {pkg.highlights.length > 0 ? (
          <ul className="mt-4 space-y-2">
            {pkg.highlights.slice(0, 3).map((highlight) => (
              <li key={highlight} className="flex items-start gap-2 text-sm text-charcoal-soft">
                <svg
                  className="mt-1 h-3.5 w-3.5 shrink-0 text-forest"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M20 6L9 17l-5-5" />
                </svg>
                {highlight}
              </li>
            ))}
          </ul>
        ) : null}

        <div className="mt-6 border-t border-line pt-5">
          {pkg.startingPrice > 0 ? (
            <p className="text-sm text-charcoal-soft">
              From{" "}
              <span className="font-display text-2xl text-forest">
                {formatMoney(pkg.startingPrice, pkg.currency)}
              </span>{" "}
              <span className="text-xs">/ person</span>
            </p>
          ) : (
            <p className="text-sm text-charcoal-soft">Pricing available on request</p>
          )}
        </div>

        <div className="mt-4 flex gap-3">
          <Link
            href={`/packages/${pkg.slug}`}
            className="flex-1 rounded-full border border-forest/30 py-2.5 text-center text-sm font-semibold text-forest transition-colors hover:bg-forest hover:text-ivory"
          >
            View Package
          </Link>
          <Link
            href={`/book?package=${pkg.slug}`}
            className="flex-1 rounded-full bg-terracotta py-2.5 text-center text-sm font-semibold text-ivory transition-colors hover:bg-terracotta-dark"
          >
            Book Now
          </Link>
        </div>
      </div>
    </article>
  );
}
