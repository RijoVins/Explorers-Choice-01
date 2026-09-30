import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Container } from "@/components/ui/Container";
import { SafeImage } from "@/components/cards/SafeImage";
import { getHotelBySlug, getHotels } from "@/lib/hotels";
import { formatMoney } from "@/lib/bookingMeta";

export const revalidate = 60;
export const dynamicParams = true;

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const result = await getHotelBySlug(slug);
  if (!result.ok || !result.data) return { title: "Hotel not found" };
  return {
    title: result.data.name,
    description: result.data.tagline || result.data.description,
  };
}

export default async function HotelDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const result = await getHotelBySlug(slug);
  if (!result.ok) throw new Error(result.error);
  const hotel = result.data;
  if (!hotel) notFound();

  // Warm the list cache so the page revalidates cheaply.
  void getHotels();

  const priceLine =
    hotel.pricePerNight > 0 ? (
      <>
        From {formatMoney(hotel.pricePerNight, hotel.currency)}
        <span className="ml-2 text-sm font-sans font-normal text-ivory/70">/ night</span>
      </>
    ) : (
      <span className="font-display text-2xl text-ivory/90">Rates on request</span>
    );

  return (
    <>
      {/* Hero */}
      <section className="relative h-[60vh] min-h-[380px] overflow-hidden">
        <SafeImage
          src={hotel.image}
          alt={hotel.name}
          placeholder="/images/hotel-placeholder.svg"
          sizes="100vw"
          className="object-cover"
          priority
        />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-dark/60 via-forest-dark/10 to-transparent" />
        <Container className="relative z-10 flex h-full flex-col justify-end pb-14">
          {hotel.location ? (
            <span className="mb-3 inline-flex w-fit rounded-full bg-ivory/90 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-forest">
              {hotel.location}
            </span>
          ) : null}
          <h1 className="font-display text-5xl leading-tight text-ivory sm:text-6xl">{hotel.name}</h1>
          <p className="mt-2 font-display text-2xl text-ivory/90">{priceLine}</p>
        </Container>
      </section>

      {/* Content */}
      <section className="py-16 sm:py-20">
        <Container className="grid gap-12 lg:grid-cols-[1.2fr_0.8fr] lg:gap-16">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
              About this hotel
            </p>
            {hotel.tagline ? (
              <h2 className="mt-4 font-display text-3xl leading-snug text-forest sm:text-4xl">
                {hotel.tagline}
              </h2>
            ) : null}
            {hotel.description ? (
              <p className="mt-6 max-w-2xl text-lg leading-relaxed text-charcoal-soft">
                {hotel.description}
              </p>
            ) : null}

            {hotel.highlights.length > 0 && (
              <div className="mt-10">
                <h3 className="font-display text-2xl text-forest">Highlights</h3>
                <ul className="mt-4 space-y-3">
                  {hotel.highlights.map((h) => (
                    <li key={h} className="flex items-start gap-3 text-charcoal-soft">
                      <svg className="mt-1 h-4 w-4 shrink-0 text-terracotta" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                        <path d="M20 6L9 17l-5-5" />
                      </svg>
                      <span>{h}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {hotel.amenities.length > 0 && (
              <div className="mt-10">
                <h3 className="font-display text-2xl text-forest">Amenities</h3>
                <ul className="mt-4 grid gap-2 sm:grid-cols-2">
                  {hotel.amenities.map((a) => (
                    <li key={a} className="flex items-center gap-2 text-sm text-charcoal-soft">
                      <span className="h-1.5 w-1.5 rounded-full bg-terracotta" />
                      {a}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <aside className="h-fit rounded-2xl border border-line bg-cream p-6 shadow-card lg:sticky lg:top-6">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
              Book this hotel
            </p>
            {hotel.pricePerNight > 0 ? (
              <>
                <p className="mt-4 font-display text-3xl text-forest">
                  {formatMoney(hotel.pricePerNight, hotel.currency)}
                </p>
                <p className="text-sm text-charcoal-soft">per night</p>
              </>
            ) : (
              <p className="mt-4 font-display text-2xl text-forest">Rates on request</p>
            )}
            <Link
              href={`/book?hotel=${hotel.slug}`}
              className="mt-6 block w-full rounded-full bg-terracotta py-3 text-center text-sm font-semibold text-ivory transition-colors hover:bg-terracotta-dark"
            >
              Book Now
            </Link>
            <Link
              href="/hotels"
              className="mt-3 block w-full rounded-full border border-line py-3 text-center text-sm font-semibold text-charcoal-soft transition-colors hover:text-forest"
            >
              ← Back to hotels
            </Link>
          </aside>
        </Container>
      </section>
    </>
  );
}
