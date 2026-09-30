"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import {
  buildDocumentDownloadUrl,
  fetchBookingDetail,
  fetchPackageDetail,
  type BookingDetail,
  type PackageDetail,
} from "@/lib/account";
import type { ItineraryDay } from "@/lib/account";
import {
  formatDate,
  formatMoney,
  paymentStatusLabel,
  statusLabel,
} from "@/lib/bookingMeta";
import { Container } from "@/components/ui/Container";
import { SupportPanel } from "@/components/account/SupportPanel";

const TIMELINE_STEPS = ["PENDING", "PENDING_CONFIRMATION", "CONFIRMED", "PAYMENT_PENDING", "PAID", "COMPLETED"];
const TIMELINE_LABELS = ["Booking requested", "Awaiting confirmation", "Confirmed", "Payment", "Ready to travel", "Completed"];

function Timeline({ currentStatus }: { currentStatus: string }) {
  const currentIdx = TIMELINE_STEPS.indexOf(currentStatus);
  return (
    <ol className="mt-5 space-y-3" aria-label="Booking status timeline">
      {TIMELINE_STEPS.map((step, idx) => {
        const reached = currentIdx >= idx;
        const active = currentIdx === idx;
        return (
          <li key={step} className="flex items-start gap-3">
            <span className={`mt-1 flex h-4 w-4 shrink-0 items-center justify-center rounded-full border-2 ${reached ? "border-forest bg-forest" : "border-line bg-ivory"}`}>
              <span className="h-2 w-2 rounded-full bg-ivory" />
            </span>
            <div>
              <p className={`text-sm font-semibold ${reached ? "text-forest" : "text-charcoal-soft"}`}>{TIMELINE_LABELS[idx]}</p>
              {active && <p className="mt-0.5 text-xs text-terracotta">Current status</p>}
            </div>
          </li>
        );
      })}
    </ol>
  );
}

function ItinerarySection({ days, travelDate }: { days: ItineraryDay[]; travelDate: string }) {
  const start = new Date(`${travelDate}T00:00:00`);
  return (
    <section className="rounded-2xl border border-line bg-cream p-6">
      <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Itinerary</p>
      <p className="mt-1 text-sm text-charcoal-soft">Your day-by-day plan, from {formatDate(travelDate)}.</p>
      <ol className="mt-6 space-y-6" aria-label="Day by day itinerary">
        {days.map((day, idx) => {
          const date = new Date(start);
          date.setDate(start.getDate() + (day.day_number - 1));
          return (
            <li key={day.day_number} className="relative flex gap-4">
              {idx < days.length - 1 && <span className="absolute left-[15px] top-9 h-[calc(100%-20px)] w-px bg-line" aria-hidden="true" />}
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-forest/20 bg-ivory text-xs font-bold text-forest">
                {day.day_number}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-baseline justify-between gap-1">
                  <h3 className="font-semibold text-forest">Day {day.day_number} · {day.title}</h3>
                  <span className="text-xs text-charcoal-soft">{date.toLocaleDateString(undefined, { month: "short", day: "numeric" })}</span>
                </div>
                {day.description && <p className="mt-1 text-sm text-charcoal-soft">{day.description}</p>}
                {day.activities.length > 0 && (
                  <ul className="mt-2 flex flex-wrap gap-1.5">
                    {day.activities.map((activity) => (
                      <li key={activity} className="rounded-full bg-forest/5 px-3 py-1 text-xs font-medium text-forest">{activity}</li>
                    ))}
                  </ul>
                )}
                <dl className="mt-3 grid gap-2 text-xs text-charcoal-soft sm:grid-cols-3">
                  {day.meals && <div><dt className="font-semibold text-forest">Meals</dt><dd>{day.meals}</dd></div>}
                  {day.accommodation && <div><dt className="font-semibold text-forest">Stay</dt><dd>{day.accommodation}</dd></div>}
                  {day.transportation && <div><dt className="font-semibold text-forest">Transport</dt><dd>{day.transportation}</dd></div>}
                </dl>
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

function TripInfoSection({ pkg }: { pkg: PackageDetail }) {
  return (
    <section className="rounded-2xl border border-line bg-cream p-6">
      <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Trip information</p>
      <div className="mt-4 space-y-4 text-sm">
        {pkg.accommodation_summary && (
          <div>
            <p className="font-semibold text-forest">Hotels &amp; stays</p>
            <p className="mt-1 text-charcoal-soft">{pkg.accommodation_summary}</p>
          </div>
        )}
        {pkg.transportation_summary && (
          <div>
            <p className="font-semibold text-forest">Transportation</p>
            <p className="mt-1 text-charcoal-soft">{pkg.transportation_summary}</p>
          </div>
        )}
        {pkg.meal_summary && (
          <div>
            <p className="font-semibold text-forest">Meals</p>
            <p className="mt-1 text-charcoal-soft">{pkg.meal_summary}</p>
          </div>
        )}
        {pkg.included.length > 0 && (
          <div>
            <p className="font-semibold text-forest">Included</p>
            <ul className="mt-2 grid gap-1.5 sm:grid-cols-2">
              {pkg.included.map((item) => (
                <li key={item} className="flex items-start gap-2 text-charcoal-soft">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-forest" aria-hidden="true" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}
        {pkg.excluded.length > 0 && (
          <div>
            <p className="font-semibold text-forest">Not included</p>
            <ul className="mt-2 grid gap-1.5 sm:grid-cols-2">
              {pkg.excluded.map((item) => (
                <li key={item} className="flex items-start gap-2 text-charcoal-soft">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-terracotta" aria-hidden="true" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}
        {pkg.important_information.length > 0 ? (
          <div className="rounded-xl border border-terracotta/20 bg-sand-light/40 p-4">
            <p className="font-semibold text-forest">Important information</p>
            <ul className="mt-2 space-y-1.5 text-charcoal-soft">
              {pkg.important_information.map((item) => (
                <li key={item} className="flex items-start gap-2">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-terracotta" aria-hidden="true" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </section>
  );
}

function useBookingDetail(bookingId: number | null) {
  const [data, setData] = useState<BookingDetail | null>(null);
  const [pkg, setPkg] = useState<PackageDetail | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(bookingId !== null);

  useEffect(() => {
    if (bookingId === null) return;
    let cancelled = false;
    fetchBookingDetail(bookingId)
      .then(async (booking) => {
        if (cancelled) return;
        setData(booking);
        if (booking.package_slug) {
          try {
            setPkg(await fetchPackageDetail(booking.package_slug));
          } catch {
            setPkg(null);
          }
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err?.message ?? "Booking not found.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [bookingId]);

  return { data, pkg, error, loading };
}

export default function BookingDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id: idStr } = use(params);
  const bookingId = /^\d+$/.test(idStr) ? Number(idStr) : null;
  const { data, pkg, error, loading } = useBookingDetail(bookingId);

  if (loading) return <Container className="py-20 text-center text-charcoal-soft">Loading trip details…</Container>;
  if (bookingId === null) {
    return <Container className="py-20 text-center text-charcoal-soft">That booking reference is not valid.</Container>;
  }
  if (error || !data) return <Container className="py-20 text-center text-charcoal-soft">{error || "Booking not found"}</Container>;

  const paidAmount = data.payments.filter((p) => p.status === "PAID").reduce((sum, p) => sum + p.amount, 0);
  const remainingAmount = Math.max(0, data.total - paidAmount);
  const travellers = data.adults + data.children + data.infants;

  return (
    <main className="py-6 sm:py-10">
      <Link href="/account/bookings" className="mb-6 inline-flex items-center gap-1.5 text-sm font-semibold text-terracotta hover:underline">
        <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M19 12H5M12 19l-7-7 7-7" /></svg>
        All bookings
      </Link>

      <section className="border-b border-line pb-6 sm:mb-8 sm:border-0 sm:pb-0">
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Booking {data.booking_reference}</p>
        <h1 className="mt-2 font-display text-3xl leading-tight text-forest sm:text-5xl">{data.destination_name}</h1>
        <p className="mt-2 text-charcoal-soft">{data.package_name} · {formatDate(data.travel_date)} · {travellers} traveller{travellers !== 1 ? "s" : ""}</p>
        <div className="mt-4 flex flex-wrap gap-3">
          <span className="rounded-full bg-ivory px-3 py-1 text-xs font-semibold text-forest">{statusLabel(data.status)}</span>
          <span className="rounded-full bg-sand-light px-3 py-1 text-xs font-semibold text-charcoal-soft">{paymentStatusLabel(data.payment_status)}</span>
        </div>
      </section>

      <div className="mt-8 grid gap-10 lg:grid-cols-[minmax(0,1fr)_360px] lg:gap-14">
        <div className="min-w-0 space-y-8">
          {/* Trip */}
          <section className="rounded-2xl border border-line bg-cream p-6">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Trip</p>
            <dl className="mt-4 grid gap-4 text-sm sm:grid-cols-2">
              <div><dt className="text-charcoal-soft">Package</dt><dd className="font-semibold text-forest">{data.package_name}</dd></div>
              <div><dt className="text-charcoal-soft">Destination</dt><dd className="font-semibold text-forest">{data.destination_name}</dd></div>
              <div><dt className="text-charcoal-soft">Travel date</dt><dd className="font-semibold text-forest">{formatDate(data.travel_date)}</dd></div>
              <div><dt className="text-charcoal-soft">Duration</dt><dd className="font-semibold text-forest">{data.duration_days} days</dd></div>
              <div><dt className="text-charcoal-soft">Travellers</dt><dd className="font-semibold text-forest">{data.adults} adults{data.children ? `, ${data.children} children` : ""}{data.infants ? `, ${data.infants} infants` : ""}</dd></div>
              <div><dt className="text-charcoal-soft">Departure</dt><dd className="font-semibold text-forest">{data.departure_information || "—"}</dd></div>
              <div><dt className="text-charcoal-soft">Special requirements</dt><dd className="font-semibold text-forest">{data.special_requirements || "—"}</dd></div>
              {data.notes && <div className="sm:col-span-2"><dt className="text-charcoal-soft">Notes</dt><dd className="font-semibold text-forest">{data.notes}</dd></div>}
            </dl>
          </section>

          {/* Payments summary (mobile-first, mirrored on desktop aside) */}
          <section className="rounded-2xl border border-line bg-cream p-6 lg:hidden">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Payments</p>
            <PaymentsSummary booking={data} paidAmount={paidAmount} remainingAmount={remainingAmount} />
          </section>

          {/* Itinerary */}
          {pkg && pkg.itinerary.length > 0 && (
            <ItinerarySection days={pkg.itinerary} travelDate={data.travel_date} />
          )}

          {/* Trip information */}
          {pkg && (
            <TripInfoSection pkg={pkg} />
          )}

          {/* Status */}
          <section className="rounded-2xl border border-line bg-cream p-6" aria-label="Booking status">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Status</p>
            <Timeline currentStatus={data.status} />
          </section>

          {/* Documents */}
          <section className="rounded-2xl border border-line bg-cream p-6">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Documents</p>
            {data.documents.length === 0 ? (
              <p className="mt-4 text-sm text-charcoal-soft">Your travel documents will appear here once your booking is confirmed.</p>
            ) : (
              <div className="mt-4 space-y-3">
                {data.documents.map((doc) => (
                  <a key={doc.id} href={buildDocumentDownloadUrl(doc.id)} className="flex items-center justify-between rounded-xl border border-line bg-white p-4 text-sm transition-colors hover:border-terracotta/40">
                    <div>
                      <p className="font-semibold text-forest">{doc.title}</p>
                      <p className="text-charcoal-soft">{doc.document_type.replace("_", " ")}</p>
                    </div>
                    <svg className="h-4 w-4 shrink-0 text-terracotta" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v12m0 0l-4-4m4 4l4-4" /></svg>
                  </a>
                ))}
              </div>
            )}
          </section>
        </div>

        <aside className="space-y-6 lg:sticky lg:top-24 lg:h-fit">
          <div className="hidden rounded-2xl border border-line bg-cream p-6 lg:block">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Payments</p>
            <PaymentsSummary booking={data} paidAmount={paidAmount} remainingAmount={remainingAmount} />
          </div>

          <SupportPanel
            message="Your travel planner can answer questions about this booking and confirm next steps."
            whatsappMessage={`Hello Explorers Choice, I have a question about my booking ${data.booking_reference}.`}
          />
        </aside>
      </div>
    </main>
  );
}

function PaymentsSummary({
  booking,
  paidAmount,
  remainingAmount,
}: {
  booking: BookingDetail;
  paidAmount: number;
  remainingAmount: number;
}) {
  return (
    <>
      <div className="mt-4 space-y-3 border-y border-line py-4 text-sm">
        <p><span className="text-charcoal-soft">Total</span><strong className="float-right text-forest">{formatMoney(booking.total, booking.currency)}</strong></p>
        <p><span className="text-charcoal-soft">Paid</span><strong className="float-right text-forest">{formatMoney(paidAmount, booking.currency)}</strong></p>
        <p><span className="text-charcoal-soft">Remaining</span><strong className="float-right text-forest">{formatMoney(remainingAmount, booking.currency)}</strong></p>
      </div>
      {booking.payments.length > 0 && (
        <ul className="mt-4 space-y-2 text-xs text-charcoal-soft">
          {booking.payments.map((payment, idx) => (
            <li key={idx} className="flex items-center justify-between gap-2">
              <span className="truncate">{payment.status === "PAID" ? "✓" : "•"} {formatMoney(payment.amount, payment.currency)}{payment.provider_reference ? ` · ${payment.provider_reference}` : ""}</span>
              <span className="shrink-0 font-semibold text-forest">{paymentStatusLabel(payment.status)}</span>
            </li>
          ))}
        </ul>
      )}
      <p className="mt-4 text-xs text-charcoal-soft">Status: {paymentStatusLabel(booking.payment_status)}</p>
    </>
  );
}