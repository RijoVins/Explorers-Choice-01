import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Container } from "@/components/ui/Container";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { Button } from "@/components/ui/Button";
import { PackageCard } from "@/components/cards/PackageCard";
import { BookNowCta } from "@/components/cta/BookNowCta";
import { getPackageBySlug, getPackages, formatMoney } from "@/lib/catalog";
import { SmartImage } from "@/components/ui/SmartImage";

export const revalidate = 60;

/**
 * Package pages are fully data-driven, so the slug set changes whenever the
 * admin publishes something new. Return no static params and let Next render
 * on demand (with ISR) instead of shipping a hardcoded list of demo slugs.
 */
export const dynamicParams = true;

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const result = await getPackageBySlug(slug);
  if (!result.ok || !result.data) return { title: "Package not found" };
  return {
    title: result.data.name,
    description: result.data.summary,
  } satisfies Metadata;
}

const Tick = ({ className }: { className?: string }) => (
  <svg
    className={className}
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
);

export default async function PackageDetail({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const result = await getPackageBySlug(slug);
  // An API outage must not 404 a real, published page.
  if (!result.ok) throw new Error(result.error);
  const pkg = result.data;
  if (!pkg) notFound();

  const allPackages = await getPackages();
  const related = allPackages.ok
    ? allPackages.data
        .filter((p) => p.destinationSlug === pkg.destinationSlug && p.slug !== slug)
        .slice(0, 2)
    : [];

  const priceLine =
    pkg.startingPrice > 0 ? (
      <>
        From{" "}
        <span className="font-display text-xl">
          {formatMoney(pkg.startingPrice, pkg.currency)}
        </span>{" "}
        per person
      </>
    ) : (
      <>Pricing available on request</>
    );

  return (
    <>
      {/* Hero */}
      <section className="relative h-[65vh] min-h-[400px] overflow-hidden">
        <SmartImage
          src={pkg.image}
          alt={pkg.name}
          sizes="100vw"
          className="object-cover"
          priority
        />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-dark/65 via-forest-dark/15 to-transparent" />
        <Container className="relative z-10 flex h-full flex-col justify-end pb-14">
          {pkg.country ? (
            <span className="mb-3 inline-flex w-fit rounded-full bg-ivory/90 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-forest">
              {pkg.country}
            </span>
          ) : null}
          <h1 className="font-display text-5xl leading-tight text-ivory sm:text-6xl">
            {pkg.name}
          </h1>
          <p className="mt-2 text-sm uppercase tracking-wide text-ivory/80">
            {[pkg.durationDays > 0 ? pkg.duration : null, priceLine]
              .filter(Boolean)
              .join(" · ")}
          </p>
        </Container>
      </section>

      {/* Content */}
      <section className="py-16 sm:py-20">
        <Container className="grid gap-12 lg:grid-cols-[1.2fr_0.8fr] lg:gap-16">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
              The journey
            </p>
            <p className="mt-4 max-w-2xl text-lg leading-relaxed text-charcoal-soft">
              {pkg.summary}
            </p>

            {pkg.highlights.length > 0 ? (
              <div className="mt-10">
                <h3 className="font-display text-2xl text-forest">Highlights</h3>
                <ul className="mt-4 space-y-3">
                  {pkg.highlights.map((h) => (
                    <li key={h} className="flex items-start gap-3 text-charcoal-soft">
                      <Tick className="mt-1 h-4 w-4 shrink-0 text-terracotta" />
                      <span>{h}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            {pkg.itinerary.length > 0 ? (
              <div className="mt-12">
                <SectionHeading eyebrow="Day by day" title="Your itinerary" />
                <div className="mt-8 space-y-6">
                  {pkg.itinerary.map((day) => (
                    <div
                      key={day.day}
                      className="flex gap-5 rounded-2xl border border-line bg-cream p-5 sm:p-6"
                    >
                      <span className="font-display text-lg text-terracotta sm:text-xl">{day.day}</span>
                      <div>
                        <h4 className="font-semibold text-forest">{day.title}</h4>
                        <p className="mt-1 text-sm leading-relaxed text-charcoal-soft">
                          {day.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="mt-12 rounded-2xl border border-dashed border-line p-8 text-center">
                <h3 className="font-display text-2xl text-forest">Itinerary coming soon</h3>
                <p className="mt-2 text-sm text-charcoal-soft">
                  Our team is still finalising the day-by-day plan for this journey.
                </p>
              </div>
            )}

            {pkg.included.length > 0 ? (
              <div className="mt-12">
                <h3 className="font-display text-2xl text-forest">What&apos;s included</h3>
                <ul className="mt-4 space-y-3">
                  {pkg.included.map((item) => (
                    <li key={item} className="flex items-start gap-3 text-charcoal-soft">
                      <Tick className="mt-1 h-4 w-4 shrink-0 text-forest" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            {pkg.excluded.length > 0 ? (
              <div className="mt-12">
                <h3 className="font-display text-2xl text-forest">Not included</h3>
                <ul className="mt-4 space-y-3">
                  {pkg.excluded.map((item) => (
                    <li key={item} className="flex items-start gap-3 text-charcoal-soft">
                      <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-terracotta" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            {pkg.importantInformation.length > 0 ? (
              <div className="mt-12 rounded-2xl border border-line bg-sand/50 p-6">
                <h3 className="font-display text-xl text-forest">Important information</h3>
                <ul className="mt-3 space-y-2 text-sm text-charcoal-soft">
                  {pkg.importantInformation.map((item) => (
                    <li key={item} className="flex items-start gap-2">
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-terracotta" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>

          {/* Booking sidebar */}
          <div className="h-fit rounded-2xl border border-line bg-cream p-8 shadow-card">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Starting from</p>
            {pkg.startingPrice > 0 ? (
              <p className="mt-2">
                <span className="font-display text-4xl text-forest">
                  {formatMoney(pkg.startingPrice, pkg.currency)}
                </span>{" "}
                <span className="text-sm text-charcoal-soft">/ person</span>
              </p>
            ) : (
              <p className="mt-2 font-display text-2xl text-forest">
                On request
              </p>
            )}
            <div className="mt-6 space-y-3 text-sm">
              {pkg.durationDays > 0 ? (
                <div className="flex justify-between border-b border-line/60 pb-3">
                  <span className="text-charcoal-soft">Duration</span>
                  <span className="font-semibold text-forest">{pkg.duration}</span>
                </div>
              ) : null}
              {pkg.destination ? (
                <div className="flex justify-between border-b border-line/60 pb-3">
                  <span className="text-charcoal-soft">Destination</span>
                  <span className="font-semibold text-forest">{pkg.destination}</span>
                </div>
              ) : null}
            </div>
            <div className="mt-8 flex flex-col gap-3">
              <Button href={`/book?package=${slug}`} variant="primary" size="md" className="w-full">
                Book Now
              </Button>
              {pkg.destinationSlug ? (
                <Link
                  href={`/destinations/${pkg.destinationSlug}`}
                  className="rounded-full border border-forest/30 py-3 text-center text-sm font-semibold text-forest transition-colors hover:bg-forest hover:text-ivory"
                >
                  View {pkg.destination || "destination"}
                </Link>
              ) : null}
            </div>
            <p className="mt-6 text-xs text-center text-charcoal-soft">
              Or speak to a planner:{" "}
              <Link href="/contact" className="font-semibold text-terracotta hover:underline">
                Get in touch
              </Link>
            </p>
          </div>
        </Container>
      </section>

      {/* Related packages */}
      {related.length > 0 && (
        <section className="border-t border-line bg-ivory-warm py-16 sm:py-20">
          <Container>
            <SectionHeading eyebrow="More journeys" title={`More in ${pkg.destination}`} />
            <div className="mt-12 grid gap-7 sm:grid-cols-2">
              {related.map((rp) => (
                <PackageCard key={rp.id} pkg={rp} />
              ))}
            </div>
          </Container>
        </section>
      )}

      <BookNowCta />
    </>
  );
}
