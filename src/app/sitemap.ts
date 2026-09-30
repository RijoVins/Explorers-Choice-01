import type { MetadataRoute } from "next";
import { getStories } from "@/lib/stories";
import { getDestinations, getPackages } from "@/lib/catalog";

const BASE = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

const staticRoutes = [
  "",
  "/destinations",
  "/packages",
  "/about",
  "/stories",
  "/faq",
  "/contact",
  "/book",
];

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const entries: MetadataRoute.Sitemap = staticRoutes.map((path) => ({
    url: `${BASE}${path}`,
    changeFrequency: path === "" ? "weekly" : "monthly",
    priority: path === "" ? 1 : 0.8,
  }));

  // Stories are addressed by numeric id, never slugs.
  const stories = await getStories();
  for (const story of stories.ok ? stories.data : []) {
    entries.push({
      url: `${BASE}/stories/${story.id}`,
      changeFrequency: "monthly",
      priority: 0.6,
    });
  }

  const destinations = await getDestinations();
  for (const destination of destinations.ok ? destinations.data : []) {
    entries.push({
      url: `${BASE}/destinations/${destination.slug}`,
      changeFrequency: "monthly",
      priority: 0.7,
    });
  }

  const packages = await getPackages();
  for (const pkg of packages.ok ? packages.data : []) {
    entries.push({
      url: `${BASE}/packages/${pkg.slug}`,
      changeFrequency: "monthly",
      priority: 0.7,
    });
  }

  return entries;
}