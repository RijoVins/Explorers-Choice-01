"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useMyBookings } from "@/hooks/useMyBookings";
import { fetchBookingDetail, type BookingDetail } from "@/lib/account";
import { formatMoney, paymentStatusLabel } from "@/lib/bookingMeta";
import { SupportPanel } from "@/components/account/SupportPanel";
import { LoadingState, EmptyState, ErrorState } from "@/components/ui/States";

type CurrencyTally = {
  paid: number;
  outstanding: number;
  paidCount: number;
  outstandingCount: number;
};

/**
 * True outstanding balances need the recorded payments, not just the summary's
 * payment_status flag. A PARTIALLY_PAID booking's full total is *not* the
 * outstanding amount — that would over-charge the traveller by whatever they
 * already paid. So partial statuses fetch their detail record to sum PAID
 * payments before reporting balances per currency.
 */
function usePaymentTotals() {
  const { bookings, loading, error } = useMyBookings();
  const [details, setDetails] = useState<Record<number, BookingDetail>>({});
  const [detailError, setDetailError] = useState<string>("");

  useEffect(() => {
    if (bookings.length === 0) return;
    let cancelled = false;
    const partialIds = bookings
      .filter((b) => b.payment_status === "PARTIALLY_PAID")
      .map((b) => b.id);
    if (partialIds.length === 0) return;
    Promise.all(
      partialIds.map((id) =>
        fetchBookingDetail(id).catch(() => null),
      ),
    )
      .then((results) => {
        if (cancelled) return;
        const map: Record<number, BookingDetail> = {};
        for (const detail of results) {
          if (detail) map[detail.id] = detail;
        }
        setDetails(map);
      })
      .catch(() => {
        if (!cancelled) setDetailError("Some payment balances could not be loaded.");
      });
    return () => {
      cancelled = true;
    };
  }, [bookings]);

  const totals = useMemo(() => {
    const tally: Record<string, CurrencyTally> = {};
    for (const b of bookings) {
      const c = b.currency || "USD";
      const bucket = (tally[c] ??= { paid: 0, outstanding: 0, paidCount: 0, outstandingCount: 0 });
      if (b.payment_status === "PAID") {
        bucket.paid += b.total;
        bucket.paidCount += 1;
      } else if (b.payment_status === "PENDING_CONFIRMATION" || b.payment_status === "PENDING") {
        bucket.outstanding += b.total;
        bucket.outstandingCount += 1;
      } else if (b.payment_status === "PARTIALLY_PAID") {
        const detail = details[b.id];
        const alreadyPaid = detail
          ? detail.payments.filter((p) => p.status === "PAID").reduce((sum, p) => sum + p.amount, 0)
          : 0;
        bucket.outstanding += Math.max(0, b.total - alreadyPaid);
        bucket.outstandingCount += 1;
      }
    }
    return tally;
  }, [bookings, details]);

  return { totals, currencies: Object.keys(totals), error: error || detailError, loading };
}

export default function PaymentsPage() {
  const { totals, currencies, error, loading } = usePaymentTotals();
  const { bookings } = useMyBookings();

  return (
    <>
      <section className="border-b border-line pb-6 sm:mb-8 sm:border-0 sm:pb-0">
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
          Financial overview
        </p>
        <h1 className="mt-2 font-display text-4xl leading-tight text-forest sm:text-5xl">
          Payments
        </h1>
        <p className="mt-3 max-w-2xl text-charcoal-soft">
          Your outstanding and completed payments across all journeys.
        </p>
      </section>

      {loading ? (
        <LoadingState label="Loading payments…" />
      ) : error ? (
        <div className="mt-8">
          <ErrorState message={error} />
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2">
          {currencies.length === 0 ? (
            <>
              <div className="rounded-2xl border border-line bg-cream p-6">
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Paid</p>
                <p className="mt-3 font-display text-3xl text-forest">—</p>
                <p className="mt-1 text-sm text-charcoal-soft">Nothing recorded yet.</p>
              </div>
              <div className="rounded-2xl border border-line bg-cream p-6">
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Outstanding</p>
                <p className="mt-3 font-display text-3xl text-forest">—</p>
                <p className="mt-1 text-sm text-charcoal-soft">Nothing recorded yet.</p>
              </div>
            </>
          ) : (
            currencies.map((c) => {
              const { paid, outstanding, paidCount, outstandingCount } = totals[c];
              return (
                <div key={c} className="rounded-2xl border border-line bg-cream p-6 col-span-1">
                  <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
                    Summary ({c})
                  </p>
                  <div className="mt-4 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-charcoal-soft">Paid</span>
                      <span className="font-semibold text-forest">
                        {formatMoney(paid, c)} ({paidCount} booking{paidCount !== 1 ? "s" : ""})
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-charcoal-soft">Outstanding</span>
                      <span className="font-semibold text-forest">
                        {formatMoney(outstanding, c)} ({outstandingCount} booking{outstandingCount !== 1 ? "s" : ""})
                      </span>
                    </div>
                    {paid === 0 && outstanding === 0 && (
                      <p className="mt-1 text-xs text-charcoal-soft">
                        No payments recorded in {c} yet.
                      </p>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {!loading && !error && bookings.length === 0 ? (
        <div className="mt-8">
          <EmptyState
            title="No payments to display yet"
            message="Payment information will appear once your booking is confirmed."
          />
        </div>
      ) : !loading && !error && bookings.length > 0 ? (
        <div className="mt-8 space-y-4">
          {bookings.map((b) => (
            <Link
              key={b.id}
              href={`/account/bookings/${b.id}`}
              className="flex flex-col gap-3 rounded-2xl border border-line bg-cream p-6 transition-colors hover:border-terracotta/40 sm:flex-row sm:items-center sm:justify-between"
            >
              <div>
                <p className="font-semibold text-forest">{b.package_name}</p>
                <p className="text-sm text-charcoal-soft">{b.booking_reference} · {b.travel_date}</p>
              </div>
              <div className="flex items-center gap-4">
                <span className="rounded-full bg-ivory px-3 py-1 text-xs font-semibold text-forest">
                  {paymentStatusLabel(b.payment_status)}
                </span>
                <span className="font-display text-lg text-forest">{formatMoney(b.total, b.currency)}</span>
              </div>
            </Link>
          ))}
        </div>
      ) : null}

      <div className="mt-12">
        <SupportPanel
          message="Talk to Explorers Choice if you have questions about a payment or booking cost."
          whatsappMessage="Hello Explorers Choice, I have a question about a payment or booking cost."
        />
      </div>
    </>
  );
}