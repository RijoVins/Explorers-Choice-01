"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { adminApi, type Dashboard } from "@/lib/admin";
import { formatMoney, paymentStatusLabel } from "@/lib/bookingMeta";

export default function AdminDashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    adminApi
      .dashboard()
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load the dashboard."));
  }, []);

  if (error) {
    return <p className="rounded-xl border border-terracotta/30 bg-terracotta/10 p-4 text-sm text-charcoal">{error}</p>;
  }
  if (!data) {
    return <p className="text-charcoal-soft">Loading dashboard…</p>;
  }

  const metrics = [
    { label: "New enquiries", value: data.new_enquiries, href: "/admin/enquiries?status=NEW" },
    { label: "Pending bookings", value: data.pending_bookings, href: "/admin/bookings" },
    { label: "Confirmed bookings", value: data.confirmed_bookings, href: "/admin/bookings" },
    { label: "Trips next 30 days", value: data.upcoming_trips, href: "/admin/bookings" },
  ];

  return (
    <>
      <section className="border-b border-line pb-6 sm:mb-8 sm:border-0 sm:pb-0">
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Workspace overview</p>
        <h1 className="mt-2 font-display text-4xl leading-tight text-forest sm:text-5xl">Good day.</h1>
        <p className="mt-3 max-w-2xl text-charcoal-soft">
          {data.new_enquiries > 0
            ? `You have ${data.new_enquiries} new enquiry${data.new_enquiries !== 1 ? "ies" : "y"} waiting for a reply.`
            : "Nothing urgent needs your attention right now."}
        </p>
      </section>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((m) => (
          <Link key={m.label} href={m.href} className="rounded-2xl border border-line bg-cream p-6 transition-colors hover:border-terracotta/40">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">{m.label}</p>
            <p className="mt-3 font-display text-4xl text-forest">{m.value}</p>
          </Link>
        ))}
      </div>

      <div className="mt-10 grid gap-8 lg:grid-cols-2">
        <section className="rounded-2xl border border-line bg-cream p-6">
          <div className="flex items-baseline justify-between">
            <h2 className="font-display text-2xl text-forest">Today&apos;s focus</h2>
          </div>
          {data.today_actions.length === 0 ? (
            <p className="mt-4 text-sm text-charcoal-soft">No departures or follow-ups scheduled for the next 30 days.</p>
          ) : (
            <ul className="mt-4 space-y-3">
              {data.today_actions.map((action) => (
                <li key={`${action.kind}-${action.id}`}>
                  <Link href={action.href} className="flex items-start justify-between gap-3 rounded-xl border border-line bg-white p-4 transition-colors hover:border-terracotta/40">
                    <div>
                      <p className="text-sm font-semibold text-forest">{action.title}</p>
                      <p className="mt-0.5 text-xs text-charcoal-soft">{action.kind === "booking_departure" ? "Upcoming departure" : "Follow-up due"}</p>
                    </div>
                    <span className="shrink-0 text-xs font-semibold text-terracotta">{action.when}</span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="rounded-2xl border border-line bg-cream p-6">
          <h2 className="font-display text-2xl text-forest">Recent payments</h2>
          {data.recent_payments.length === 0 ? (
            <p className="mt-4 text-sm text-charcoal-soft">No payments recorded yet.</p>
          ) : (
            <ul className="mt-4 space-y-3">
              {data.recent_payments.map((p, idx) => (
                <li key={idx} className="flex items-center justify-between gap-3 rounded-xl border border-line bg-white p-4">
                  <div>
                    <p className="text-sm font-semibold text-forest">{p.booking_ref}</p>
                    <p className="mt-0.5 text-xs text-charcoal-soft">
                      {new Date(p.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-display text-lg text-forest">
                      {formatMoney(p.amount, p.currency)}
                    </p>
                    <span className="mt-0.5 inline-block rounded-full bg-ivory px-2.5 py-0.5 text-[11px] font-semibold text-forest">
                      {paymentStatusLabel(p.status)}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </>
  );
}