import { apiGet, type ApiResult } from "@/lib/apiClient";

/**
 * Hotels read model.
 *
 * `getMergedHotels` previously unioned every API hotel with eight hardcoded
 * sample properties, so an empty database still published fabricated nightly
 * rates and star ratings. The API is now the only source of truth.
 *
 * Note: the `hotels` table has no rating column, so `rating` is intentionally
 * absent here rather than faked as 0. The UI hides rating UI when it is not
 * present instead of showing invented stars.
 */

export type ApiHotel = {
  id: number;
  slug: string;
  name: string;
  location: string;
  destination: string;
  tagline: string;
  description: string;
  image: string;
  pricePerNight: number;
  currency: string;
  amenities: string[];
  highlights: string[];
};

const str = (value: unknown, fallback = ""): string =>
  value === null || value === undefined ? fallback : String(value);

const strArray = (value: unknown): string[] =>
  Array.isArray(value) ? value.map((item) => String(item)) : [];

export function toHotel(api: Record<string, unknown>): ApiHotel {
  const price = Number(api.price_per_night);
  return {
    id: Number(api.id) || 0,
    slug: str(api.slug),
    name: str(api.name),
    location: str(api.location),
    destination: str(api.destination),
    tagline: str(api.tagline),
    description: str(api.description),
    image: str(api.image),
    pricePerNight: Number.isFinite(price) ? price : 0,
    currency: str(api.currency, "USD"),
    amenities: strArray(api.amenities),
    highlights: strArray(api.highlights),
  };
}

export async function getHotels(): Promise<ApiResult<ApiHotel[]>> {
  const result = await apiGet<Record<string, unknown>[]>("/hotels");
  if (!result.ok) return result;
  return { ok: true, data: result.data.map(toHotel) };
}

export async function getHotelBySlug(
  slug: string,
): Promise<ApiResult<ApiHotel | null>> {
  const result = await apiGet<Record<string, unknown>>(
    `/hotels/${encodeURIComponent(slug)}`,
  );
  if (!result.ok) {
    return result.status === 404 ? { ok: true, data: null } : result;
  }
  return { ok: true, data: toHotel(result.data) };
}
