import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Container } from "@/components/ui/Container";
import { Button } from "@/components/ui/Button";
import { SafeImage } from "@/components/cards/SafeImage";
import { BookNowCta } from "@/components/cta/BookNowCta";
import { getStory } from "@/lib/stories";

export const revalidate = 60;
export const dynamicParams = true;

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const id = Number(slug);
  if (!Number.isInteger(id)) return { title: "Story not found" };
  const result = await getStory(id);
  if (!result.ok || !result.data) return { title: "Story not found" };
  return {
    title: `${result.data.customerName}'s Story`,
    description: result.data.excerpt || result.data.story.slice(0, 160),
  } satisfies Metadata;
}

export default async function StoryDetail({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const id = Number(slug);
  if (!Number.isInteger(id)) notFound();

  const result = await getStory(id);
  if (!result.ok) throw new Error(result.error);
  const story = result.data;
  if (!story) notFound();

  const paragraphs = story.story.split(/\n{2,}/).map((p) => p.trim()).filter(Boolean);
  const image = story.photos[0] || null;

  return (
    <>
      <Container className="max-w-3xl pt-14">
        <Link
          href="/stories"
          className="text-sm font-semibold text-forest underline-offset-4 hover:underline"
        >
          ← All customer stories
        </Link>
        <div className="mt-8">
          <div className="flex items-center gap-3 text-xs font-semibold uppercase tracking-wide text-charcoal-soft">
            {story.packageName ? (
              <>
                <span className="text-terracotta">{story.packageName}</span>
                <span aria-hidden="true">·</span>
              </>
            ) : null}
            {story.destination ? <span>{story.destination}</span> : null}
          </div>
          <h1 className="mt-4 font-display text-4xl leading-tight text-forest sm:text-5xl">
            {story.customerName}&apos;s story
          </h1>
          {story.excerpt ? (
            <p className="mt-6 font-display text-2xl leading-relaxed text-charcoal">
              &quot;{story.excerpt}&quot;
            </p>
          ) : null}
        </div>

        {image ? (
          <div className="mt-10 overflow-hidden rounded-3xl">
            <SafeImage
              src={image}
              alt={story.customerName}
              sizes="(min-width: 768px) 48rem, 100vw"
              className="h-auto w-full object-cover"
            />
          </div>
        ) : null}

        {paragraphs.length > 0 ? (
          <article className="mt-10 space-y-6">
            {paragraphs.map((paragraph, index) => (
              <p key={index} className="text-lg leading-relaxed text-charcoal-soft">
                {paragraph}
              </p>
            ))}
          </article>
        ) : null}

        <div className="mt-12 border-t border-line pt-6">
          <p className="text-sm text-charcoal-soft">
            — <span className="font-semibold text-charcoal">{story.customerName}</span>
            {story.packageName ? <> travelled on {story.packageName}</> : " travelled with Explorers Choice"}
          </p>
        </div>

        <div className="mt-10 flex flex-col gap-3 sm:flex-row">
          <Button href="/book#trip" variant="primary" size="md">
            Book Now
          </Button>
          <Button href="/packages" variant="outline" size="md">
            Browse Packages
          </Button>
        </div>
      </Container>

      <BookNowCta
        heading="Ready to write your own story?"
        subtext="Talk to a real travel planner and start planning a journey worth remembering."
      />
    </>
  );
}