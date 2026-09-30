import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Container } from "@/components/ui/Container";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { PackageCard } from "@/components/cards/PackageCard";
import { SafeImage } from "@/components/cards/SafeImage";
import { BookNowCta } from "@/components/cta/BookNowCta";
import { getDestinationBySlug, getPackages } from "@/lib/catalog";
import { BackButton } from "@/components/ui/BackButton";

export const revalidate = 60;
export const dynamicParams = true;

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const result = await getDestinationBySlug(slug);
  if (!result.ok || !result.data) return { title: "Destination not found" };
  return {
    title: result.data.name,
    description: result.data.tagline,
  } satisfies Metadata;
}

export default async function DestinationDetail({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const result = await getDestinationBySlug(slug);
  if (!result.ok) throw new Error(result.error);
  const destination = result.data;
  if (!destination) notFound();

  const allPackages = await getPackages();
  const relatedPackages = allPackages.ok
    ? allPackages.data.filter((p) => p.destinationSlug === destination.slug)
    : [];

  // Only show facts the record actually carries.
  const facts = [
    { label: "Country", value: destination.country },
    { label: "Region", value: destination.region },
    { label: "Best time to visit", value: destination.bestTime },
    { label: "Recommended duration", value: destination.recommendedDuration },
  ].filter((fact) => fact.value);

  return (
    <>
      {/* Back Button */}
      <div className="absolute top-4 left-4 z-20">
        <BackButton
          label=""
          variant="ghost"
          size="sm"
          className="!bg-white/20 !text-white hover:!bg-white/30 backdrop-blur-sm"
        />
      </div>

      {/* Hero */}
      <section className="relative h-[70vh] min-h-[440px] overflow-hidden">
        <SafeImage
          src={destination.image}
          alt={destination.name}
          sizes="100vw"
          className="object-cover"
          priority
        />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-dark/60 via-forest-dark/10 to-transparent" />
        <Container className="relative z-10 flex h-full flex-col justify-end pb-14">
          {destination.region ? (
            <Badge variant="forest" size="md" className="mb-4 w-fit">
              {destination.region}
            </Badge>
          ) : null}
          <h1 className="font-display text-5xl leading-tight text-ivory sm:text-6xl">
            {destination.name}
          </h1>
          {destination.country ? (
            <p className="mt-2 text-sm uppercase tracking-wide text-ivory/80">{destination.country}</p>
          ) : null}
        </Container>
      </section>

      {/* Detail Content */}
      <section className="py-16 sm:py-20">
        <Container className="grid gap-12 lg:grid-cols-[1.2fr_0.8fr] lg:gap-16">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
              About the destination
            </p>
            {destination.tagline ? (
              <h2 className="mt-4 font-display text-3xl leading-snug text-forest sm:text-4xl">
                {destination.tagline}
              </h2>
            ) : null}
            {destination.description ? (
              <p className="mt-6 max-w-2xl text-lg leading-relaxed text-charcoal-soft">
                {destination.description}
              </p>
            ) : null}

            {destination.highlights.length > 0 ? (
              <div className="mt-10">
                <h3 className="font-display text-2xl text-forest">Highlights</h3>
                <ul className="mt-4 space-y-3">
                  {destination.highlights.map((highlight) => (
                    <li key={highlight} className="flex items-start gap-3 text-charcoal-soft">
                      <svg className="mt-1 h-4 w-4 shrink-0 text-terracotta" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                        <path d="M20 6L9 17l-5-5" />
                      </svg>
                      <span>{highlight}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            {destination.thingsToDo.length > 0 ? (
              <div className="mt-12">
                <h3 className="font-display text-2xl text-forest">Things to do</h3>
                <ul className="mt-4 grid gap-3 sm:grid-cols-2">
                  {destination.thingsToDo.map((item) => (
                    <li key={item} className="flex items-start gap-3 text-charcoal-soft">
                      <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-terracotta" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            {destination.travelInformation.length > 0 ? (
              <div className="mt-12 rounded-2xl border border-line bg-sand/50 p-6">
                <h3 className="font-display text-xl text-forest">Travel information</h3>
                <ul className="mt-3 space-y-2 text-sm text-charcoal-soft">
                  {destination.travelInformation.map((item) => (
                    <li key={item} className="flex items-start gap-2">
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-terracotta" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>

          {/* Sidebar */}
          <div className="rounded-2xl border border-line bg-cream p-8 shadow-card">
            <h3 className="font-display text-xl text-forest">At a glance</h3>
            {facts.length > 0 ? (
              <div className="mt-5 space-y-4">
                {facts.map((fact) => (
                  <div key={fact.label} className="flex justify-between gap-4 border-b border-line/60 pb-3 text-sm">
                    <span className="text-charcoal-soft">{fact.label}</span>
                    <span className="text-right font-semibold text-forest">{fact.value}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="mt-4 text-sm text-charcoal-soft">
                Our team is still adding the details for this destination.
              </p>
            )}
            <div className="mt-8 flex flex-col gap-3">
              <Button href={`/book?destination=${slug}`} variant="primary" size="md" className="w-full">
                Book Now
              </Button>
              <Button href="/packages" variant="outline" size="md" className="w-full">
                View All Packages
              </Button>
            </div>
          </div>
        </Container>
      </section>

      {/* Related packages */}
      {relatedPackages.length > 0 ? (
        <section className="border-t border-line bg-ivory-warm py-16 sm:py-20">
          <Container>
            <SectionHeading
              eyebrow="Packages"
              title={`Journeys to ${destination.name}`}
              description={`Our curated travel packages for ${destination.name}, planned by our local experts.`}
            />
            <div className="mt-12 grid gap-7 sm:grid-cols-2 lg:grid-cols-3">
              {relatedPackages.map((pkg) => (
                <PackageCard key={pkg.id} pkg={pkg} />
              ))}
            </div>
          </Container>
        </section>
      ) : (
        <section className="border-t border-line bg-ivory-warm py-16 sm:py-20">
          <Container>
            <div className="rounded-2xl border border-dashed border-line py-16 text-center">
              <h3 className="font-display text-2xl text-forest">
                No published journeys for {destination.name} yet
              </h3>
              <p className="mx-auto mt-2 max-w-md text-sm text-charcoal-soft">
                Our planners are still building itineraries for this destination. Get in touch and
                we&apos;ll design one for you.
              </p>
              <Button href="/contact" variant="outline" size="md" className="mt-6">
                Speak to a planner
              </Button>
            </div>
          </Container>
        </section>
      )}

      <BookNowCta />
    </>
  );
}
