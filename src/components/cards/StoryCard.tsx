import Link from "next/link";
import { SafeImage } from "@/components/cards/SafeImage";
import { formatTravelDate, type CustomerStory } from "@/lib/stories";

export function StoryCard({
  story,
  featured = false,
}: {
  story: CustomerStory;
  featured?: boolean;
}) {
  const url = `/stories/${story.id}`;
  const image = story.photos[0] || null;
  return (
    <article
      className={`group flex flex-col overflow-hidden rounded-2xl border border-line bg-cream shadow-card ${
        featured ? "md:flex-row" : ""
      }`}
    >
      <Link
        href={url}
        className={`relative block overflow-hidden bg-sand ${
          featured ? "aspect-[4/3] md:flex-none md:w-1/2" : "aspect-[3/2]"
        }`}
      >
        <SafeImage
          src={image}
          alt={story.packageName || `${story.customerName}'s story`}
          sizes="(min-width: 1024px) 50vw, 100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-dark/30 to-transparent" />
      </Link>

      <div className={`flex flex-1 flex-col p-6 ${featured ? "md:p-10 md:justify-center" : ""}`}>
        <div className="flex items-center gap-3 text-xs font-semibold uppercase tracking-wide text-charcoal-soft">
          <span className="text-terracotta">
            {story.packageName || story.destination || "Explorers Choice"}
          </span>
          {story.travelDate ? (
            <span className="text-charcoal-soft">{formatTravelDate(story.travelDate)}</span>
          ) : null}
        </div>
        <Link href={url}>
          <h3
            className={`font-display text-forest transition-colors group-hover:text-forest-light ${
              featured ? "mt-4 text-3xl leading-tight sm:text-4xl" : "mt-3 text-xl leading-snug"
            }`}
          >
            {story.customerName}&apos;s story
          </h3>
        </Link>
        <p className="mt-3 text-sm leading-relaxed text-charcoal-soft line-clamp-3">
          {story.excerpt || "Read the full story."}
        </p>
        <p className="mt-5 text-sm font-semibold text-charcoal">— {story.customerName}</p>
        <Link
          href={url}
          className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-forest"
        >
          Read the story
          <svg
            className="h-4 w-4 transition-transform group-hover:translate-x-1"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </Link>
      </div>
    </article>
  );
}