import Link from "next/link";
import { Container } from "@/components/ui/Container";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { DestinationCard } from "@/components/cards/DestinationCard";
import { getDestinations } from "@/lib/catalog";

export async function FeaturedDestinations() {
  const result = await getDestinations();
  const featured = result.ok
    ? result.data.filter((d) => d.isFeatured).slice(0, 4)
    : [];

  return (
    <section className="py-20 sm:py-24" aria-label="Featured destinations">
      <Container>
        <div className="flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-end">
          <SectionHeading
            eyebrow="Where to go"
            title="Destinations we can't stop talking about"
            description="Every place we feature has been travelled, re-travelled and refined by our team. These are the ones our clients keep coming back for."
          />
          <Link
            href="/destinations"
            className="shrink-0 text-sm font-semibold text-forest underline-offset-4 hover:underline"
          >
            View all destinations
          </Link>
        </div>

        {featured.length > 0 && (
          <div className="mt-12 grid gap-7 sm:grid-cols-2 lg:grid-cols-4">
            {featured.map((destination) => (
              <DestinationCard key={destination.id} destination={destination} />
            ))}
          </div>
        )}
      </Container>
    </section>
  );
}