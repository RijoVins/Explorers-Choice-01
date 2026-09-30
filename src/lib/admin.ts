import type { UserProfile } from "@/lib/auth";
import type { BookingMode } from "@/lib/bookingMeta";
import { formatMoney } from "@/lib/bookingMeta";

import { getApiBaseUrl } from "@/lib/api";

export class AdminApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "AdminApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    const apiBase = getApiBaseUrl();
    response = await fetch(`${apiBase}/api${path}`, {
      credentials: "include",
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    });
  } catch {
    throw new AdminApiError("Could not reach the server. Check your connection and try again.", 0);
  }
  if (!response.ok) {
    let detail = "Something went wrong.";
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      /* keep default */
    }
    throw new AdminApiError(detail, response.status);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export type Role = "CUSTOMER" | "TRAVEL_AGENT" | "MANAGER" | "ACCOUNTANT" | "ADMIN";

export type StaffMember = {
  id: number;
  email: string;
  full_name: string;
  phone: string;
  country: string;
  role: Role;
  is_staff: boolean;
  is_active: boolean;
  created_at: string;
  password?: never;
};

export type BookingListItem = {
  id: number;
  booking_reference: string;
  package_name: string;
  destination_name: string;
  travel_date: string;
  adults: number;
  children: number;
  infants: number;
  total: number;
  currency: string;
  status: string;
  payment_status: string;
  booking_mode: BookingMode;
  created_at: string;
};

export type Traveller = { traveller_type: string; quantity: number };
export type PaymentRecord = {
  id: number;
  booking_id: number;
  amount: number;
  currency: string;
  status: string;
  provider: string;
  provider_reference: string;
  created_at: string;
  updated_at: string;
};
export type DocumentRecord = { id: number; document_type: string; title: string; file_name: string; created_at: string };
export type BookingNote = { id: number; booking_id: number; body: string; created_at: string; author: UserProfile | null };
export type BookingUser = { id: number; email: string; full_name: string; role: Role; is_staff: boolean };

export type BookingAdminDetail = {
  id: number;
  booking_reference: string;
  package_id: number;
  package_slug: string;
  package_name: string;
  destination_name: string;
  duration_days: number;
  travel_date: string;
  adults: number;
  children: number;
  infants: number;
  departure_information: string;
  country: string;
  special_requirements: string;
  notes: string;
  subtotal: number;
  taxes: number;
  total: number;
  currency: string;
  status: string;
  payment_status: string;
  booking_mode: BookingMode;
  created_at: string;
  updated_at: string;
  full_name: string;
  email: string;
  phone: string;
  user: BookingUser | null;
  travellers: Traveller[];
  internal_notes: BookingNote[];
  payments: PaymentRecord[];
  documents: DocumentRecord[];
};

export const ENQUIRY_STAGES = ["NEW", "CONTACTED", "REQUIREMENTS_COLLECTED", "PLANNING", "QUOTE_SENT", "NEGOTIATION", "WON", "LOST"] as const;
export type EnquiryStage = (typeof ENQUIRY_STAGES)[number];

export type Enquiry = {
  id: number;
  customer_name: string;
  email: string;
  phone: string;
  country: string;
  destination_interest: string;
  package_id: number | null;
  package_name: string;
  travel_date_from: string | null;
  travel_date_to: string | null;
  travellers: number;
  budget: string;
  message: string;
  notes: string;
  status: EnquiryStage;
  assigned_staff_id: number | null;
  assigned_staff: StaffMember | null;
  last_contact_at: string | null;
  next_action: string;
  next_action_at: string | null;
  created_at: string;
  updated_at: string;
};

export type CustomerSummary = {
  id: number;
  email: string;
  full_name: string;
  phone: string;
  country: string;
  role: Role;
  requested_role: "CUSTOMER" | "TRAVEL_AGENT" | null;
  is_active: boolean;
  created_at: string;
  booking_count: number;
  enquiry_count: number;
  total_spent: number;
};

export type CustomerDetail = CustomerSummary & {
  bookings: BookingAdminDetail[];
  enquiries: Enquiry[];
};

export type Offer = {
  id: number;
  title: string;
  code: string;
  description: string;
  discount_type: "PERCENT" | "FIXED";
  discount_value: number;
  package_id: number | null;
  package_name: string;
  valid_from: string | null;
  valid_to: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type DestinationOption = {
  id: number;
  name: string;
  slug: string;
  country: string;
};

export type DestinationAdmin = {
  id: number;
  name: string;
  slug: string;
  country: string;
  region: string;
  short_description: string;
  description: string;
  hero_image: string;
  gallery: string[];
  best_time: string;
  recommended_duration: string;
  highlights: string[];
  things_to_do: string[];
  travel_information: string[];
  is_featured: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type DestinationFormPayload = Omit<
  DestinationAdmin,
  "id" | "created_at" | "updated_at"
>;

export type Package = {
  id: number;
  destination_id: number;
  name: string;
  slug: string;
  short_description: string;
  description: string;
  duration_days: number;
  duration_nights: number;
  starting_price: number;
  currency: string;
  hero_image: string;
  gallery: string[];
  highlights: string[];
  included: string[];
  excluded: string[];
  accommodation_summary: string;
  transportation_summary: string;
  meal_summary: string;
  cancellation_policy: string;
  important_information: string[];
  booking_mode: "REQUEST_ONLY" | "INSTANT_BOOKING";
  is_featured: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  destination?: DestinationOption | null;
  itinerary?: unknown[];
  faqs?: unknown[];
};

export type PackageFormPayload = {
  destination_id: number;
  name: string;
  slug: string;
  short_description: string;
  description: string;
  duration_days: number;
  duration_nights: number;
  starting_price: number;
  currency: string;
  hero_image: string;
  gallery: string[];
  highlights: string[];
  included: string[];
  excluded: string[];
  accommodation_summary: string;
  transportation_summary: string;
  meal_summary: string;
  cancellation_policy: string;
  important_information: string[];
  booking_mode: "REQUEST_ONLY" | "INSTANT_BOOKING";
  is_featured: boolean;
  is_active: boolean;
};

export type ItineraryDayInput = {
  day_number: number;
  title: string;
  description: string;
  activities: string[];
  meals: string;
  accommodation: string;
  transportation: string;
};

export type CustomerStory = {
  id: number;
  customer_name: string;
  destination: string;
  package_id: number | null;
  package_name: string;
  story: string;
  photos: string[];
  travel_date: string | null;
  is_featured: boolean;
  is_published: boolean;
  created_at: string;
  updated_at: string;
};

export type AuditLogEntry = {
  id: number;
  user_id: number | null;
  username: string;
  action: string;
  entity: string;
  entity_id: string;
  details: string;
  created_at: string;
};

export type Setting = { key: string; value: Record<string, unknown>; updated_at: string };

export type HotelAdmin = {
  id: number;
  owner_id: number;
  slug: string;
  name: string;
  location: string;
  destination: string;
  tagline: string;
  description: string;
  image: string;
  price_per_night: number;
  currency: string;
  amenities: string[];
  highlights: string[];
  is_published: boolean;
  created_at: string;
  updated_at: string;
};

export type HotelFormPayload = {
  name: string;
  location: string;
  destination: string;
  tagline: string;
  description: string;
  image: string;
  price_per_night: number;
  currency: string;
  amenities: string[];
  highlights: string[];
  is_published: boolean;
};

export type Dashboard = {
  new_enquiries: number;
  pending_bookings: number;
  confirmed_bookings: number;
  upcoming_trips: number;
  total_bookings: number;
  today_actions: { kind: string; id: number; title: string; when: string; href: string }[];
  recent_payments: { booking_ref: string; amount: number; currency: string; status: string; created_at: string }[];
  recent_customers: { id: number; name: string; email: string; last_activity: string }[];
  booking_status_counts: Record<string, number>;
};

export const adminApi = {
  dashboard: () => request<Dashboard>("/admin/dashboard"),

  bookings: (status?: string) =>
    request<BookingListItem[]>(`/admin/bookings${status ? `?status=${encodeURIComponent(status)}` : ""}`),
  booking: (id: number) => request<BookingAdminDetail>(`/admin/bookings/${id}`),
  updateBookingStatus: (id: number, status: string, payment_status?: string) =>
    request<BookingListItem>(`/admin/bookings/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status, payment_status }),
    }),
  updatePaymentStatus: (id: number, status: string, payment_status: string) =>
    request<BookingListItem>(`/admin/bookings/${id}/payment`, {
      method: "PATCH",
      body: JSON.stringify({ status, payment_status }),
    }),
  addNote: (bookingId: number, body: string) =>
    request<BookingNote>(`/admin/bookings/${bookingId}/notes`, { method: "POST", body: JSON.stringify({ body }) }),
  recordPayment: (data: { booking_id: number; amount: number; currency?: string; status?: string; provider?: string; provider_reference?: string }) =>
    request<PaymentRecord>("/admin/payments", { method: "POST", body: JSON.stringify(data) }),

  enquiries: (status?: string) =>
    request<Enquiry[]>(`/admin/enquiries${status ? `?enquiry_status=${encodeURIComponent(status)}` : ""}`),
  enquiry: (id: number) => request<Enquiry>(`/admin/enquiries/${id}`),
  updateEnquiry: (
    id: number,
    data: Partial<Pick<Enquiry, "status" | "assigned_staff_id" | "next_action" | "next_action_at" | "notes" | "budget" | "destination_interest" | "last_contact_at">>
  ) => request<Enquiry>(`/admin/enquiries/${id}`, { method: "PATCH", body: JSON.stringify(data) }),

  customers: () => request<CustomerSummary[]>("/admin/customers"),
  customer: (id: number) => request<CustomerDetail>(`/admin/customers/${id}`),
  deleteCustomer: (id: number) => request<void>(`/admin/customers/${id}`, { method: "DELETE" }),

  offers: () => request<Offer[]>("/admin/offers"),
  createOffer: (data: Partial<Offer>) => request<Offer>("/admin/offers", { method: "POST", body: JSON.stringify(data) }),
  updateOffer: (id: number, data: Partial<Offer>) => request<Offer>(`/admin/offers/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteOffer: (id: number) => request<void>(`/admin/offers/${id}`, { method: "DELETE" }),

  stories: () => request<CustomerStory[]>("/admin/customer-stories"),
  createStory: (data: Partial<CustomerStory>) => request<CustomerStory>("/admin/customer-stories", { method: "POST", body: JSON.stringify(data) }),
  updateStory: (id: number, data: Partial<CustomerStory>) => request<CustomerStory>(`/admin/customer-stories/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteStory: (id: number) => request<void>(`/admin/customer-stories/${id}`, { method: "DELETE" }),

  adminHotels: () => request<HotelAdmin[]>("/admin/hotels"),
  createHotel: (data: HotelFormPayload) =>
    request<HotelAdmin>("/admin/hotels", { method: "POST", body: JSON.stringify(data) }),
  updateHotel: (id: number, data: Partial<HotelFormPayload>) =>
    request<HotelAdmin>(`/admin/hotels/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteHotel: (id: number) =>
    request<void>(`/admin/hotels/${id}`, { method: "DELETE" }),

  packages: () => request<Package[]>("/admin/packages"),
  package: (id: number) => request<Package>(`/admin/packages/${id}`),
  createPackage: (data: PackageFormPayload) => request<Package>("/admin/packages", { method: "POST", body: JSON.stringify(data) }),
  updatePackage: (id: number, data: Partial<PackageFormPayload>) => request<Package>(`/admin/packages/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  replaceItinerary: (packageId: number, days: ItineraryDayInput[]) =>
    request<Package>(`/admin/packages/${packageId}/itinerary`, {
      method: "PUT",
      body: JSON.stringify(days),
    }),
  deletePackage: (id: number, hard = false) =>
    request<void>(`/admin/packages/${id}${hard ? "?hard=true" : ""}`, { method: "DELETE" }),

  destinations: () => request<DestinationOption[]>("/destinations"),
  adminDestinations: () => request<DestinationAdmin[]>("/admin/destinations"),
  createDestination: (data: DestinationFormPayload) =>
    request<DestinationAdmin>("/admin/destinations", { method: "POST", body: JSON.stringify(data) }),
  updateDestination: (id: number, data: Partial<DestinationFormPayload>) =>
    request<DestinationAdmin>(`/admin/destinations/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteDestination: (id: number, hard = false) =>
    request<void>(`/admin/destinations/${id}${hard ? "?hard=true" : ""}`, { method: "DELETE" }),

  staff: () => request<StaffMember[]>("/admin/staff"),
  createStaff: (data: { email: string; password: string; full_name: string; phone?: string; country?: string; role: Role }) =>
    request<StaffMember>("/admin/staff", { method: "POST", body: JSON.stringify(data) }),
  updateStaff: (id: number, data: Partial<StaffMember>) => request<StaffMember>(`/admin/staff/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteStaff: (id: number) => request<void>(`/admin/staff/${id}`, { method: "DELETE" }),
  promoteCustomer: (id: number, role: Exclude<Role, "CUSTOMER">) =>
    request<StaffMember>(`/admin/customers/${id}/role`, { method: "PATCH", body: JSON.stringify({ role }) }),
  staffAssign: () => request<StaffMember[]>("/admin/staff-assign"),

  settings: () => request<Setting[]>("/admin/settings"),
  updateSetting: (key: string, value: Record<string, unknown>) =>
    request<Setting>(`/admin/settings/${encodeURIComponent(key)}`, { method: "PUT", body: JSON.stringify({ value }) }),

  auditLog: () => request<AuditLogEntry[]>("/admin/audit-log"),
};

export async function attachDocument(bookingId: number, documentType: string, title: string, file: File): Promise<DocumentRecord> {
  const form = new FormData();
  form.append("document_type", documentType);
  form.append("title", title);
  form.append("file", file);
  let response: Response;
  try {
    const apiBase = getApiBaseUrl();
    response = await fetch(`${apiBase}/api/admin/bookings/${bookingId}/documents`, { method: "POST", credentials: "include", body: form });
  } catch {
    throw new AdminApiError("Could not reach the server. Check your connection and try again.", 0);
  }
  if (!response.ok) {
    let detail = "Could not upload the document.";
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      /* keep default */
    }
    throw new AdminApiError(detail, response.status);
  }
  return (await response.json()) as DocumentRecord;
}

export function formatWhen(value: string | null | undefined): string {
  if (!value) return "—";
  return new Date(value).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

export async function uploadPackageImage(file: File): Promise<{ url: string }> {
  const form = new FormData();
  form.append("file", file);
  let response: Response;
  try {
    const apiBase = getApiBaseUrl();
    response = await fetch(`${apiBase}/api/admin/packages/upload-image`, { method: "POST", credentials: "include", body: form });
  } catch {
    throw new AdminApiError("Could not reach the server. Check your connection and try again.", 0);
  }
  if (!response.ok) {
    let detail = "Could not upload the image.";
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      /* keep default */
    }
    throw new AdminApiError(detail, response.status);
  }
  return (await response.json()) as { url: string };
}

export function packageImageUrl(path: string): string {
  if (!path) return "";
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  const apiBase = getApiBaseUrl();
  return `${apiBase}/api${path.startsWith("/") ? "" : "/"}${path}`;
}

export function adminDocumentUrl(documentId: number): string {
  const apiBase = getApiBaseUrl();
  return `${apiBase}/api/admin/documents/${documentId}/download`;
}

/** Alias kept for the admin call sites; delegates to the canonical formatter. */
export const formatMoneyAmount = formatMoney;