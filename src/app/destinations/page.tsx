import type { Metadata } from "next";
import { Container } from "@/components/ui/Container";
import { DestinationCard } from "@/components/cards/DestinationCard";
import { EmptyState, ErrorState } from "@/components/ui/States";
import { getDestinations } from "@/lib/catalog";

export const revalidate = 60;

export const metadata: Metadata = {
  title: "Destinations",
  description:
    "Explore the destinations we know, love and keep returning to. Every place on our list has been travelled, refined and recommended by the Explorers Choice team.",
};

export default async function DestinationsPage() {
  const result = await getDestinations();

  return (
    <>
      <section className="border-b border-line bg-ivory-warm">
        <Container className="py-16 sm:py-20">
          <p className="mb-4 text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
            Where to go
          </p>
          <h1 className="font-display text-5xl leading-tight text-forest sm:text-6xl">
            Destinations
          </h1>
          <p className="mt-5 max-w-xl text-lg leading-relaxed text-charcoal-soft">
            Every place we feature has been travelled, re-travelled and refined by our team.
            These are the journeys we genuinely recommend.
          </p>
        </Container>
      </section>

      <section className="py-16 sm:py-20">
        <Container>
          {!result.ok ? (
            <ErrorState message={result.error} />
          ) : result.data.length === 0 ? (
            <EmptyState
              title="No destinations published yet"
              message="We haven't published any destinations yet. Once our team adds one it will appear here straight away."
            />
          ) : (
            <div className="grid gap-7 sm:grid-cols-2 lg:grid-cols-3">
              {result.data.map((destination) => (
                <DestinationCard key={destination.id} destination={destination} />
              ))}
            </div>
          )}
        </Container>
      </section>
    </>
  );
}
