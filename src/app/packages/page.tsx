import type { Metadata } from "next";
import { Container } from "@/components/ui/Container";
import { BookNowCta } from "@/components/cta/BookNowCta";
import { getPackages } from "@/lib/catalog";
import { EmptyState, ErrorState } from "@/components/ui/States";
import { PackageFilterGrid } from "@/components/packages/PackageFilterGrid";

export const revalidate = 60;

export const metadata: Metadata = {
  title: "Packages",
  description:
    "Browse our curated travel packages. Every journey is planned, priced and perfected with local guides, handpicked stays and a dedicated travel planner.",
};

export default async function PackagesPage() {
  const result = await getPackages();

  return (
    <>
      <section className="border-b border-line bg-ivory-warm">
        <Container className="py-16 sm:py-20">
          <p className="mb-4 text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
            Curated journeys
          </p>
          <h1 className="font-display text-5xl leading-tight text-forest sm:text-6xl">
            Travel Packages
          </h1>
          <p className="mt-5 max-w-xl text-lg leading-relaxed text-charcoal-soft">
            Thoughtfully paced, honestly priced, and designed around how you actually want to
            travel.
          </p>
        </Container>
      </section>

      <section className="py-16 sm:py-20">
        <Container>
          {!result.ok ? (
            <ErrorState message={result.error} />
          ) : result.data.length === 0 ? (
            <EmptyState
              title="No journeys published yet"
              message="We haven't published any packages yet. Once our team adds one it will appear here straight away."
            />
          ) : (
            <PackageFilterGrid initialPackages={result.data} />
          )}
        </Container>
      </section>

      <BookNowCta
        heading="Not sure where to start?"
        subtext="Tell us a destination, a feeling or nothing at all. Our travel planners will help you find the right journey."
      />
    </>
  );
}
