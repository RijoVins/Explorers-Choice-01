export type BookingStatus =
  | "PENDING"
  | "PENDING_CONFIRMATION"
  | "CONFIRMED"
  | "PAYMENT_PENDING"
  | "PARTIALLY_PAID"
  | "PAID"
  | "CANCELLED"
  | "COMPLETED";

export type PaymentStatus =
  | "NOT_REQUIRED"
  | "PENDING"
  | "PARTIALLY_PAID"
  | "PAID"
  | "FAILED"
  | "REFUNDED";

export type BookingMode = "REQUEST_ONLY" | "INSTANT_BOOKING";

export const STATUS_LABELS: Record<BookingStatus, string> = {
  PENDING: "Under review",
  PENDING_CONFIRMATION: "Awaiting confirmation",
  CONFIRMED: "Confirmed",
  PAYMENT_PENDING: "Payment pending",
  PARTIALLY_PAID: "Partially paid",
  PAID: "Paid",
  CANCELLED: "Cancelled",
  COMPLETED: "Completed",
};

export const PAYMENT_STATUS_LABELS: Record<PaymentStatus, string> = {
  NOT_REQUIRED: "No payment yet",
  PENDING: "Payment pending",
  PARTIALLY_PAID: "Partially paid",
  PAID: "Paid",
  FAILED: "Payment failed — please retry",
  REFUNDED: "Refunded",
};

export const BOOKING_MODE_LABELS: Record<BookingMode, string> = {
  REQUEST_ONLY: "Request booking",
  INSTANT_BOOKING: "Instant booking",
};

export function statusLabel(status: string): string {
  return STATUS_LABELS[status as BookingStatus] ?? status;
}

export function paymentStatusLabel(status: string): string {
  return PAYMENT_STATUS_LABELS[status as PaymentStatus] ?? status;
}

export function bookingModeLabel(mode: string): string {
  return BOOKING_MODE_LABELS[mode as BookingMode] ?? mode;
}

/**
 * Single canonical money formatter for the whole site.
 *
 * The backend stores a real ISO currency code on every money-bearing row
 * (Package, Booking, Payment, Hotel, TrainBooking, CabBooking), so the code is
 * always taken from the record — never hardcoded to a symbol. An unrecognised
 * or empty code degrades to "CODE 1,234" instead of throwing, because a bad
 * currency on one record must not blank out an entire page.
 */
export function formatMoney(amount: number, currency?: string | null): string {
  const code = (currency || "USD").trim().toUpperCase();
  const value = Number.isFinite(amount) ? amount : 0;
  try {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: code,
      maximumFractionDigits: 0,
    }).format(value);
  } catch {
    return `${code} ${value.toLocaleString("en-US")}`;
  }
}

/**
 * `formatDate` is for date-only values (travel dates, check-ins). Passing a
 * bare date string to `new Date()` treats it as UTC midnight, which renders as
 * the previous day for anyone west of Greenwich, so the local date is built
 * component-by-component instead.
 */
export function formatDate(date: string): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(date.trim());
  const parsed = match
    ? new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]))
    : new Date(date);
  if (Number.isNaN(parsed.getTime())) return date;
  return parsed.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}
