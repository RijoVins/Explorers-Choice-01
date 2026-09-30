"use client";

import { useState, useMemo } from "react";
import { PackageCard } from "@/components/cards/PackageCard";
import type { CatalogPackage } from "@/lib/catalog";

type DestinationOption = { slug: string; name: string };

type PackageFilterGridProps = {
  initialPackages: CatalogPackage[];
};

export function PackageFilterGrid({ initialPackages }: PackageFilterGridProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedDestination, setSelectedDestination] = useState<DestinationOption>({
    slug: "",
    name: "",
  });
  const [sortBy, setSortBy] = useState("recommended");

  // Only destinations that actually carry a package make the dropdown. A
  // destination with zero published journeys is not a useful filter value.
  const destinations = useMemo(() => {
    const map = new Map<string, string>();
    for (const pkg of initialPackages) {
      if (pkg.destinationSlug && pkg.destination) {
        map.set(pkg.destinationSlug, pkg.destination);
      }
    }
    return Array.from(map, ([slug, name]) => ({ slug, name })).sort((a, b) =>
      a.name.localeCompare(b.name),
    );
  }, [initialPackages]);

  const filteredAndSortedPackages = useMemo(() => {
    let result = [...initialPackages];

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (p) =>
          p.name.toLowerCase().includes(q) ||
          p.country.toLowerCase().includes(q) ||
          p.destination.toLowerCase().includes(q) ||
          p.highlights.some((h) => h.toLowerCase().includes(q)),
      );
    }

    if (selectedDestination.slug) {
      result = result.filter((p) => p.destinationSlug === selectedDestination.slug);
    }

    if (sortBy === "recommended") {
      // "Recommended" means admin-featured, not an invented popularity score.
      result.sort((a, b) => Number(b.isFeatured) - Number(a.isFeatured));
    } else if (sortBy === "price_asc") {
      result.sort((a, b) => a.startingPrice - b.startingPrice);
    } else if (sortBy === "price_desc") {
      result.sort((a, b) => b.startingPrice - a.startingPrice);
    } else if (sortBy === "duration_asc") {
      result.sort((a, b) => a.durationDays - b.durationDays);
    } else if (sortBy === "duration_desc") {
      result.sort((a, b) => b.durationDays - a.durationDays);
    }

    return result;
  }, [initialPackages, searchQuery, selectedDestination, sortBy]);

  const clearFilters = () => {
    setSearchQuery("");
    setSelectedDestination({ slug: "", name: "" });
  };

  return (
    <div>
      {/* Filters Bar */}
      <div className="mb-10 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between rounded-2xl border border-line bg-cream p-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search journeys, places, or highlights..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-xl border border-line bg-white px-4 py-2.5 text-sm text-charcoal focus:border-terracotta focus:outline-none"
          />
        </div>

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
          <select
            value={selectedDestination.slug}
            onChange={(e) => {
              const next =
                destinations.find((d) => d.slug === e.target.value) ??
                { slug: "", name: "" };
              setSelectedDestination(next);
            }}
            className="rounded-xl border border-line bg-white px-4 py-2.5 text-sm text-charcoal focus:border-terracotta focus:outline-none"
          >
            <option value="">All Destinations</option>
            {destinations.map((dest) => (
              <option key={dest.slug} value={dest.slug}>
                {dest.name}
              </option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="rounded-xl border border-line bg-white px-4 py-2.5 text-sm text-charcoal focus:border-terracotta focus:outline-none"
          >
            <option value="recommended">Recommended First</option>
            <option value="price_asc">Price: Low to High</option>
            <option value="price_desc">Price: High to Low</option>
            <option value="duration_asc">Duration: Short to Long</option>
            <option value="duration_desc">Duration: Long to Short</option>
          </select>
        </div>
      </div>

      {/* Grid */}
      {filteredAndSortedPackages.length > 0 ? (
        <div className="grid gap-7 sm:grid-cols-2 lg:grid-cols-3">
          {filteredAndSortedPackages.map((pkg) => (
            <PackageCard key={pkg.id} pkg={pkg} />
          ))}
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-line py-16 text-center">
          <h3 className="font-display text-2xl text-forest">No journeys found</h3>
          <p className="mt-2 text-charcoal-soft">
            Try adjusting your search or clear your filters.
          </p>
          <button
            onClick={clearFilters}
            className="mt-6 font-semibold text-terracotta hover:underline"
          >
            Clear filters
          </button>
        </div>
      )}
    </div>
  );
}