import { apiGet, type ApiResult } from "@/lib/apiClient";
import { formatMoney } from "@/lib/bookingMeta";

// Re-exported so catalog consumers have one money formatter, not two.
export { formatMoney };

/**
 * Catalog read model.
 *
 * The API is the only source of truth. There is deliberately no fallback to
 * hardcoded sample destinations or packages: an empty database must render an
 * honest empty state, and an API failure must render an error state, not
 * fabricated travel products.
 */

const MEENAKSHI_TEMPLE_IMAGE =
  "https://images.unsplash.com/photo-1692173248120-59547c3d4653?auto=format&fit=crop&w=1600&q=80";

const IMAGE_FALLBACKS: Record<string, string> = {
  "https://images.unsplash.com/photo-1506461883276-59f2ebe600eb": MEENAKSHI_TEMPLE_IMAGE,
  "https://images.unsplash.com/photo-1583430788308-9fe346a8e869": MEENAKSHI_TEMPLE_IMAGE,
  "https://images.unsplash.com/photo-1600100598826-6b4f6ffe5d32": MEENAKSHI_TEMPLE_IMAGE,
};

function resolveImage(url: string): string {
  if (!url) return "";
  return IMAGE_FALLBACKS[url.split("?")[0]] ?? url;
}

export type ApiItineraryDay = {
  id?: number;
  package_id?: number;
  day_number: number;
  title: string;
  description: string;
  activities: string[];
  meals: string;
  accommodation: string;
  transportation: string;
};

export type ApiPackageFaq = {
  id?: number;
  question: string;
  answer: string;
  sort_order?: number;
};

export type Destination = {
  id: number;
  slug: string;
  name: string;
  country: string;
  region: string;
  tagline: string;
  description: string;
  image: string;
  bestTime: string;
  recommendedDuration: string;
  highlights: string[];
  gallery: string[];
  thingsToDo: string[];
  travelInformation: string[];
  isFeatured: boolean;
  isActive: boolean;
};

export type CatalogPackage = {
  id: number;
  slug: string;
  destinationId: number | null;
  destinationSlug: string;
  name: string;
  destination: string;
  country: string;
  durationDays: number;
  duration: string;
  startingPrice: number;
  currency: string;
  highlights: string[];
  image: string;
  summary: string;
  itinerary: { day: string; title: string; description: string }[];
  included: string[];
  excluded: string[];
  accommodationSummary: string;
  transportationSummary: string;
  mealSummary: string;
  cancellationPolicy: string;
  importantInformation: string[];
  gallery: string[];
  isFeatured: boolean;
  isActive: boolean;
  bookingMode: string;
  itineraryDays: ApiItineraryDay[];
  faqs: ApiPackageFaq[];
};

const str = (value: unknown, fallback = ""): string =>
  value === null || value === undefined ? fallback : String(value);

const strArray = (value: unknown): string[] =>
  Array.isArray(value) ? value.map((item) => String(item)) : [];

const num = (value: unknown, fallback = 0): number => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

export function toDestination(api: Record<string, unknown>): Destination {
  return {
    id: num(api.id),
    slug: str(api.slug),
    name: str(api.name),
    country: str(api.country),
    region: str(api.region),
    tagline: str(api.short_description),
    description: str(api.description),
    image: resolveImage(str(api.hero_image)),
    bestTime: str(api.best_time),
    recommendedDuration: str(api.recommended_duration),
    highlights: strArray(api.highlights),
    gallery: strArray(api.gallery).map(resolveImage),
    thingsToDo: strArray(api.things_to_do),
    travelInformation: strArray(api.travel_information),
    isFeatured: Boolean(api.is_featured),
    isActive: Boolean(api.is_active),
  };
}

export function toPackage(
  api: Record<string, unknown>,
  detail = false,
): CatalogPackage {
  const destination = api.destination as Record<string, unknown> | undefined;
  const durationDays = num(api.duration_days);
  const itinerary = Array.isArray(api.itinerary)
    ? (api.itinerary as ApiItineraryDay[])
    : [];
  const faqs = Array.isArray(api.faqs) ? (api.faqs as ApiPackageFaq[]) : [];
  return {
    id: num(api.id),
    slug: str(api.slug),
    destinationId:
      api.destination_id === null || api.destination_id === undefined
        ? null
        : num(api.destination_id),
    destinationSlug: destination?.slug ? String(destination.slug) : "",
    name: str(api.name),
    destination: destination?.name ? String(destination.name) : "",
    country: destination?.country ? String(destination.country) : "",
    durationDays,
    duration: durationDays > 0 ? `${durationDays} days` : "Duration TBC",
    startingPrice: num(api.starting_price),
    currency: str(api.currency, "INR"),
    highlights: strArray(api.highlights),
    image: resolveImage(str(api.hero_image)),
    summary: str(api.short_description || api.description),
    itinerary: itinerary.map((day) => ({
      day: `Day ${day.day_number}`,
      title: str(day.title),
      description: str(day.description),
    })),
    included: strArray(api.included),
    excluded: strArray(api.excluded),
    accommodationSummary: str(api.accommodation_summary),
    transportationSummary: str(api.transportation_summary),
    mealSummary: str(api.meal_summary),
    cancellationPolicy: str(api.cancellation_policy),
    importantInformation: strArray(api.important_information),
    gallery: strArray(api.gallery).map(resolveImage),
    isFeatured: Boolean(api.is_featured),
    isActive: Boolean(api.is_active),
    bookingMode: str(api.booking_mode, "REQUEST_ONLY"),
    itineraryDays: detail ? itinerary : [],
    faqs: detail ? faqs : [],
  };
}

// ---------------------------------------------------------------------------
// Destinations
// ---------------------------------------------------------------------------

export async function getDestinations(): Promise<ApiResult<Destination[]>> {
  const result = await apiGet<Record<string, unknown>[]>("/destinations");
  if (!result.ok) return result;
  return { ok: true, data: result.data.map(toDestination) };
}

export async function getDestinationBySlug(
  slug: string,
): Promise<ApiResult<Destination | null>> {
  const result = await apiGet<Record<string, unknown>>(
    `/destinations/${encodeURIComponent(slug)}`,
  );
  if (!result.ok) {
    return result.status === 404
      ? { ok: true, data: null }
      : result;
  }
  return { ok: true, data: toDestination(result.data) };
}

/**
 * Client-side destinations fetch for interactive pages (e.g. the spot cards on
 * /book). Failure yields `[]` — never sample records — so the section simply
 * does not render until the data genuinely exists.
 */
export async function fetchDestinationsClient(): Promise<Destination[]> {
  try {
    const { getApiBaseUrl } = await import("@/lib/api");
    const response = await fetch(`${getApiBaseUrl()}/api/destinations`, {
      credentials: "include",
      cache: "no-store",
    });
    if (!response.ok) return [];
    const data = (await response.json()) as Record<string, unknown>[];
    return data.map(toDestination);
  } catch {
    return [];
  }
}

// ---------------------------------------------------------------------------
// Packages
// ---------------------------------------------------------------------------

export async function getPackages(): Promise<ApiResult<CatalogPackage[]>> {
  const result = await apiGet<Record<string, unknown>[]>("/packages");
  if (!result.ok) return result;
  return { ok: true, data: result.data.map((item) => toPackage(item)) };
}

export async function getPackageBySlug(
  slug: string,
): Promise<ApiResult<CatalogPackage | null>> {
  const result = await apiGet<Record<string, unknown>>(
    `/packages/${encodeURIComponent(slug)}`,
  );
  if (!result.ok) {
    return result.status === 404
      ? { ok: true, data: null }
      : result;
  }
  return { ok: true, data: toPackage(result.data, true) };
}
