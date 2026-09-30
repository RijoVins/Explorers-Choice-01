"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { BookingFlow } from "@/components/booking/BookingFlow";
import { Container } from "@/components/ui/Container";
import { DestinationSpotCard } from "@/components/booking/DestinationSpotCard";
import { EmptyState } from "@/components/ui/States";
import { fetchDestinationsClient, type Destination } from "@/lib/catalog";

function BookContent() {
  const searchParams = useSearchParams();
  const destinationParam = searchParams.get("destination");
  const packageParam = searchParams.get("package");
  const [destinations, setDestinations] = useState<Destination[] | null>(null);

  useEffect(() => {
    let active = true;
    fetchDestinationsClient().then((data) => {
      if (active) setDestinations(data);
    });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (destinationParam || packageParam) {
      document.getElementById("trip")?.scrollIntoView({ behavior: "smooth" });
    }
  }, [destinationParam, packageParam]);

  const showSpots = destinations && destinations.length > 0;

  return (
    <>
      <section className="border-b border-line bg-ivory-warm">
        <Container className="py-12 sm:py-16">
          <p className="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Book your journey</p>
          <h1 className="font-display text-4xl leading-tight text-forest sm:text-6xl">Book Now</h1>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-charcoal-soft sm:text-lg">
            A clear, considered way to start your next journey. Your price is always visible before you send a request.
          </p>
        </Container>
      </section>

      {showSpots ? (
        <section className="py-10 sm:py-16">
          <Container>
            <div className="mb-10">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Popular destinations</p>
              <h2 className="mt-3 font-display text-3xl text-forest sm:text-4xl">Choose a destination to begin</h2>
              <p className="mt-3 max-w-2xl text-base leading-relaxed text-charcoal-soft">
                Pick one of the places we know best and we&apos;ll pre-select the journeys that take you there.
              </p>
            </div>
            <div className="grid gap-7 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4">
              {destinations.map((destination) => (
                <DestinationSpotCard key={destination.id} destination={destination} />
              ))}
            </div>
          </Container>
        </section>
      ) : destinations === null ? (
        <section className="py-10 sm:py-16">
          <Container>
            <EmptyState
              title="Loading destinations"
              message="Checking what's available for your journey…"
            />
          </Container>
        </section>
      ) : null}

      <section id="trip" className="scroll-mt-24 py-10 sm:py-16">
        <Container>
          <BookingFlow packageSlug={packageParam} destinationSlug={destinationParam} />
        </Container>
      </section>
    </>
  );
}

export default function BookPage() {
  return <Suspense fallback={<Container className="py-20 text-center text-charcoal-soft">Loading booking…</Container>}><BookContent /></Suspense>;
}