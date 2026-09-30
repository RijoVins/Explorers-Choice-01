"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Container } from "@/components/ui/Container";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { StoryCard } from "@/components/cards/StoryCard";
import { stories } from "@/data/stories";

const AUTOPLAY_MS = 3000;

function ChevronIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M9 6l6 6-6 6" />
    </svg>
  );
}

export function CustomerStories() {
  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(false);
  const count = stories.length;

  const goNext = useCallback(() => setIndex((current) => (current + 1) % count), [count]);
  const goPrev = useCallback(() => setIndex((current) => (current - 1 + count) % count), [count]);

  useEffect(() => {
    if (paused || count < 2) return;
    const id = setInterval(goNext, AUTOPLAY_MS);
    return () => clearInterval(id);
  }, [goNext, paused, count]);

  return (
    <section
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      className="py-20 sm:py-24"
    >
      <Container>
        <div className="flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-end">
          <SectionHeading
            eyebrow="Customer stories"
            title="Real travellers, real memories"
            description="Not testimonials plucked off a booking form—honest stories from people who travelled with us, told in their own words."
          />
          <div className="flex items-center gap-4">
            <Link
              href="/stories"
              className="shrink-0 text-sm font-semibold text-forest underline-offset-4 hover:underline"
            >
              All customer stories
            </Link>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={goPrev}
                disabled={index === 0}
                aria-label="Previous story"
                className="flex h-10 w-10 items-center justify-center rounded-full border border-line bg-ivory text-forest shadow-card transition-colors hover:border-terracotta hover:text-terracotta focus-visible:outline-terracotta disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:border-line disabled:hover:text-forest"
              >
                <ChevronIcon className="h-4 w-4 rotate-180" />
              </button>
              <button
                type="button"
                onClick={goNext}
                disabled={index === count - 1}
                aria-label="Next story"
                className="flex h-10 w-10 items-center justify-center rounded-full border border-line bg-ivory text-forest shadow-card transition-colors hover:border-terracotta hover:text-terracotta focus-visible:outline-terracotta disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:border-line disabled:hover:text-forest"
              >
                <ChevronIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        <div className="relative mt-12 overflow-hidden rounded-2xl">
          <div
            className="flex transition-transform duration-700 ease-out"
            style={{ transform: `translateX(-${index * 100}%)` }}
          >
            {stories.map((story) => (
              <div key={story.slug} className="w-full shrink-0">
                <StoryCard story={story} featured />
              </div>
            ))}
          </div>
        </div>

        <div className="mt-6 flex justify-center gap-2">
          {stories.map((story, i) => (
            <button
              key={story.slug}
              type="button"
              onClick={() => setIndex(i)}
              aria-label={`Go to story ${i + 1} of ${count}`}
              className={`h-2.5 rounded-full transition-all duration-300 ${
                i === index ? "w-8 bg-terracotta" : "w-2.5 bg-forest/20 hover:bg-forest/40"
              }`}
            />
          ))}
        </div>
      </Container>
    </section>
  );
}