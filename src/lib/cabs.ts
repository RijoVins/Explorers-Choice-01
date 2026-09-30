import { getApiBaseUrl } from "./api";

export type CabTripType = "LOCAL" | "AIRPORT_TRANSFER" | "OUTSTATION";

export const TRIP_TYPE_LABELS: Record<CabTripType, string> = {
  LOCAL: "Local / City Rental",
  AIRPORT_TRANSFER: "Airport Transfer",
  OUTSTATION: "Outstation / One Way",
};

export type CabBookingPayload = {
  trip_type: CabTripType;
  cab_type: string;
  pickup_location: string;
  drop_location: string;
  pickup_date: string;
  pickup_time: string;
  distance_kms: number;
  passengers: number;
  full_name: string;
  email: string;
  phone: string;
  special_requirements?: string;
  idempotency_key?: string;
};

export type CabBookingConfirmation = {
  id: number;
  booking_reference: string;
  trip_type: CabTripType;
  cab_type: string;
  pickup_location: string;
  drop_location: string;
  pickup_date: string;
  pickup_time: string;
  distance_kms: number;
  passengers: number;
  full_name: string;
  email: string;
  phone: string;
  special_requirements: string;
  base_fare: number;
  convenience_fee: number;
  gst: number;
  total_amount: number;
  currency: string;
  status: string;
  created_at: string;
};

export async function createCabBooking(
  payload: CabBookingPayload
): Promise<CabBookingConfirmation> {
  const res = await fetch(`${getApiBaseUrl()}/api/cabs/bookings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to place cab booking request");
  }
  return res.json();
}

export async function getCabBookingByReference(
  reference: string
): Promise<CabBookingConfirmation | null> {
  const res = await fetch(
    `${getApiBaseUrl()}/api/cabs/bookings/reference/${encodeURIComponent(reference)}`,
    { cache: "no-store", credentials: "include" }
  );
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("Could not load cab booking");
  return res.json();
}

export async function getMyCabBookings(): Promise<CabBookingConfirmation[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/cabs/my-bookings`, {
    credentials: "include",
    cache: "no-store",
  });
  if (!res.ok) return [];
  return res.json();
}