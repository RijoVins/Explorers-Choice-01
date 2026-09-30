import type { Metadata } from "next";
import { Container } from "@/components/ui/Container";
import { HotelCard } from "@/components/cards/HotelCard";
import { getHotels } from "@/lib/hotels";
import { EmptyState, ErrorState } from "@/components/ui/States";

export const metadata: Metadata = {
  title: "Hotels",
  description:
    "Handpicked stays from floating palaces to mountain retreats. Every hotel we feature has been personally tried and recommended by the Explorers Choice team.",
};

export default async function HotelsPage() {
  const result = await getHotels();

  return (
    <>
      <section className="border-b border-line bg-ivory-warm">
        <Container className="py-16 sm:py-20">
          <p className="mb-4 text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
            Where to stay
          </p>
          <h1 className="font-display text-5xl leading-tight text-forest sm:text-6xl">
            Hotels
          </h1>
          <p className="mt-5 max-w-xl text-lg leading-relaxed text-charcoal-soft">
            From floating lake palaces to Himalayan mountain retreats, these are the stays we
            genuinely love — personally tried, handpicked and recommended by our team.
          </p>
        </Container>
      </section>

      <section className="py-16 sm:py-20">
        <Container>
          {!result.ok ? (
            <ErrorState message={result.error} />
          ) : result.data.length === 0 ? (
            <EmptyState
              title="No stays published yet"
              message="We haven't published any hotels yet. Once our team adds one it will appear here straight away."
            />
          ) : (
            <div className="grid gap-7 sm:grid-cols-2 lg:grid-cols-3">
              {result.data.map((hotel) => (
                <HotelCard key={hotel.id} hotel={hotel} />
              ))}
            </div>
          )}
        </Container>
      </section>
    </>
  );
}