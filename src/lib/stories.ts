import { apiGet, type ApiResult } from "@/lib/apiClient";

/**
 * Public customer stories.
 *
 * `CustomerStory` has no slug column, so stories are addressed by their stable
 * numeric id. Public listing only returns published stories; the admin area
 * uses its own authenticated endpoints.
 */

export type CustomerStory = {
  id: number;
  customerName: string;
  destination: string;
  packageId: number | null;
  packageName: string;
  story: string;
  photos: string[];
  travelDate: string;
  isFeatured: boolean;
  isPublished: boolean;
  createdAt: string;
  excerpt: string;
};

type ApiStory = {
  id: number;
  customer_name?: string;
  destination?: string;
  package_id?: number | null;
  package_name?: string;
  story?: string;
  photos?: string[];
  travel_date?: string;
  is_featured?: boolean;
  is_published?: boolean;
  created_at?: string;
};

const EXCERPT_LENGTH = 180;

export function toCustomerStory(api: ApiStory): CustomerStory {
  const story = typeof api.story === "string" ? api.story.trim() : "";
  const excerpt =
    story.length > EXCERPT_LENGTH ? `${story.slice(0, EXCERPT_LENGTH).trimEnd()}…` : story;
  return {
    id: Number(api.id),
    customerName: api.customer_name ? String(api.customer_name) : "A traveller",
    destination: api.destination ? String(api.destination) : "",
    packageId: api.package_id ?? null,
    packageName: api.package_name ? String(api.package_name) : "",
    story,
    photos: Array.isArray(api.photos) ? api.photos.map(String) : [],
    travelDate: api.travel_date ? String(api.travel_date) : "",
    isFeatured: Boolean(api.is_featured),
    isPublished: Boolean(api.is_published),
    createdAt: api.created_at ? String(api.created_at) : "",
    excerpt,
  };
}

export async function getStories(): Promise<ApiResult<CustomerStory[]>> {
  const result = await apiGet<ApiStory[]>("/customer-stories");
  if (!result.ok) return result;
  return { ok: true, data: result.data.map(toCustomerStory) };
}

export async function getStory(id: number): Promise<ApiResult<CustomerStory | null>> {
  const result = await apiGet<ApiStory>(`/customer-stories/${id}`);
  if (!result.ok) {
    return result.status === 404 ? { ok: true, data: null } : result;
  }
  return { ok: true, data: toCustomerStory(result.data) };
}

export function formatTravelDate(value: string): string {
  if (!value) return "";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}
