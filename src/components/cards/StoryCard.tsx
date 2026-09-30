import Link from "next/link";
import { SmartImage } from "@/components/ui/SmartImage";
import { formatTravelDate } from "@/lib/stories";

export type StoryInput = {
  id?: number | string;
  slug?: string;
  image?: string;
  photos?: string[];
  title?: string;
  quote?: string;
  excerpt?: string;
  customerName?: string;
  author?: string;
  packageName?: string;
  destination?: string;
  travelDate?: string | null;
};

export function StoryCard({
  story,
  featured = false,
}: {
  story: StoryInput;
  featured?: boolean;
}) {
  const url = `/stories/${story.slug || story.id || ""}`;
  const image = story.image || (story.photos && story.photos[0]) || "";
  const name = story.customerName || story.author || "A traveller";
  const title = story.title || `${name}'s story`;
  const text = story.quote || story.excerpt || "Read the full story.";

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
        <SmartImage
          src={image}
          alt={title}
          fill
          sizes="(min-width: 1024px) 50vw, 100vw"
          className="object-cover transition-transform duration-500 group-hover:scale-105"
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
            {title}
          </h3>
        </Link>
        <p className="mt-3 text-sm leading-relaxed text-charcoal-soft line-clamp-3">
          {text}
        </p>
        <p className="mt-5 text-sm font-semibold text-charcoal">— {name}</p>
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