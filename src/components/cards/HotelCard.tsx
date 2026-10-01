import { HotelImage } from "./HotelImage";
import Link from "next/link";
import type { ApiHotel } from "@/lib/hotels";
import { formatMoney } from "@/lib/bookingMeta";

export function HotelCard({ hotel }: { hotel: ApiHotel }) {
  return (
    <article className="group flex flex-col overflow-hidden rounded-2xl border border-line bg-cream shadow-card transition-transform duration-200 hover:-translate-y-1">
      <Link href={`/hotels/${hotel.slug}`} className="relative block aspect-[3/2] overflow-hidden bg-sand">
        <HotelImage
          src={hotel.image}
          name={hotel.name}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-dark/50 to-transparent" />
        {hotel.location ? (
          <span className="absolute left-4 top-4 rounded-full bg-ivory/90 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-forest">
            {hotel.location}
          </span>
        ) : null}
      </Link>

      <div className="flex flex-1 flex-col p-6">
        <Link href={`/hotels/${hotel.slug}`}>
          <h3 className="font-display text-2xl leading-snug text-forest transition-colors group-hover:text-forest-light">
            {hotel.name}
          </h3>
          {hotel.destination ? (
            <p className="mt-1 text-sm uppercase tracking-wide text-terracotta">{hotel.destination}</p>
          ) : null}
        </Link>

        {hotel.highlights.length > 0 ? (
        <ul className="mt-4 space-y-2">
          {hotel.highlights.slice(0, 3).map((highlight) => (
            <li key={highlight} className="flex items-start gap-2 text-sm text-charcoal-soft">
              <svg
                className="mt-1 h-3.5 w-3.5 shrink-0 text-forest"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M20 6L9 17l-5-5" />
              </svg>
              {highlight}
            </li>
          ))}
        </ul>
        ) : null}

        <div className="mt-6 border-t border-line pt-5">
          {hotel.pricePerNight > 0 ? (
            <p className="text-sm text-charcoal-soft">
              From{" "}
              <span className="font-display text-2xl text-forest">
                {formatMoney(hotel.pricePerNight, hotel.currency)}
              </span>{" "}
              <span className="text-xs">/ night</span>
            </p>
          ) : (
            <p className="text-sm text-charcoal-soft">Rates available on request</p>
          )}
        </div>

        <div className="mt-4 flex gap-3">
          <Link
            href={`/hotels/${hotel.slug}`}
            className="flex-1 rounded-full border border-forest/30 py-2.5 text-center text-sm font-semibold text-forest transition-colors hover:bg-forest hover:text-ivory"
          >
            View Hotel
          </Link>
          <Link
            href={`/contact?hotel=${hotel.slug}&name=${encodeURIComponent(hotel.name)}`}
            className="flex-1 rounded-full bg-terracotta py-2.5 text-center text-sm font-semibold text-ivory transition-colors hover:bg-terracotta-dark"
          >
            Enquire Now
          </Link>
        </div>
      </div>
    </article>
  );
}
