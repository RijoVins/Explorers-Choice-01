"use client";

import { FormEvent, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { Container } from "@/components/ui/Container";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/components/providers";
import {
  createCabBooking,
  TRIP_TYPE_LABELS,
  CabBookingConfirmation,
  CabTripType,
} from "@/lib/cabs";

const fieldClasses =
  "w-full rounded-xl border border-line bg-white px-4 py-3 text-sm text-charcoal placeholder:text-charcoal-soft/60 focus:border-terracotta focus:outline-none";

const labelClasses = "block text-xs font-bold uppercase tracking-[0.14em] text-charcoal-soft";

function tomorrowStr(): string {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toISOString().split("T")[0];
}

export default function CabsPage() {
  const { user } = useAuth();

  const [tripType, setTripType] = useState<CabTripType>("AIRPORT_TRANSFER");
  const [cabType, setCabType] = useState("");
  const [pickupLocation, setPickupLocation] = useState("");
  const [dropLocation, setDropLocation] = useState("");
  const [pickupDate, setPickupDate] = useState(tomorrowStr());
  const [pickupTime, setPickupTime] = useState("10:00");
  const [distanceKms, setDistanceKms] = useState("");
  const [passengers, setPassengers] = useState(2);

  const [fullName, setFullName] = useState(user?.full_name || "");
  const [email, setEmail] = useState(user?.email || "");
  const [phone, setPhone] = useState(user?.phone || "");
  const [specialRequirements, setSpecialRequirements] = useState("");

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [confirmed, setConfirmed] = useState<CabBookingConfirmation | null>(null);

  const idempotencyRef = useRef<string | null>(null);

  const distance = useMemo(() => Math.max(0, Number(distanceKms) || 0), [distanceKms]);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");

    if (!cabType.trim()) {
      setError("Please tell us the cab type you'd prefer.");
      return;
    }
    if (!pickupLocation.trim() || !dropLocation.trim()) {
      setError("Please enter both pickup and drop locations.");
      return;
    }
    if (!pickupDate || new Date(pickupDate) <= new Date(new Date().toDateString())) {
      setError("Pickup date must be in the future.");
      return;
    }
    if (!fullName.trim() || !email.trim() || !phone.trim()) {
      setError("Please fill in your name, email, and phone number.");
      return;
    }

    if (!idempotencyRef.current) {
      idempotencyRef.current = crypto.randomUUID();
    }

    setIsSubmitting(true);
    try {
      const result = await createCabBooking({
        trip_type: tripType,
        cab_type: cabType.trim(),
        pickup_location: pickupLocation.trim(),
        drop_location: dropLocation.trim(),
        pickup_date: pickupDate,
        pickup_time: pickupTime,
        distance_kms: distance,
        passengers,
        full_name: fullName.trim(),
        email: email.trim(),
        phone: phone.trim(),
        special_requirements: specialRequirements.trim(),
        idempotency_key: idempotencyRef.current,
      });
      setConfirmed(result);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not place your request. Please try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  function reset() {
    setConfirmed(null);
    setError("");
    idempotencyRef.current = null;
  }

  return (
    <div className="min-h-screen bg-sand/30 pb-20">
      {/* Hero Banner */}
      <section className="relative overflow-hidden bg-forest py-16 text-ivory sm:py-20">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(201,122,86,0.18),transparent_60%)]" />
        <Container className="relative">
          <div className="max-w-3xl">
            <span className="inline-flex items-center gap-2 rounded-full border border-ivory/20 bg-ivory/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-ivory">
              🚖 Cab &amp; Car Rental &bull; Explorers Choice
            </span>
            <h1 className="mt-4 font-display text-4xl leading-tight text-ivory sm:text-5xl lg:text-6xl">
              Book a Cab, We Handle the Driving
            </h1>
            <p className="mt-4 text-lg text-ivory/80">
              Airport pickups, local city rides, and outstation trips with clean, verified cars.
              Send your request and our team confirms instantly over email &amp; phone.
            </p>
          </div>
        </Container>
      </section>

      <Container className="mt-8 lg:mt-12">
        {confirmed ? (
          /* Confirmation */
          <div className="mx-auto max-w-3xl overflow-hidden rounded-2xl bg-white p-6 shadow-xl ring-1 ring-black/5 sm:p-10">
            <div className="py-6 text-center">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 text-3xl text-emerald-800">
                ✓
              </div>
              <h2 className="mt-4 font-display text-2xl font-bold text-forest sm:text-3xl">
                Cab Booking Request Received!
              </h2>
              <p className="mx-auto mt-2 max-w-xl text-sm text-charcoal-soft">
                Your request has been sent to <strong>infoexplorerschoice@gmail.com</strong> and a
                copy is on its way to <strong>{confirmed.email}</strong>. Our team will be in touch
                shortly to confirm the fare and driver.
              </p>

              <div className="mt-6 rounded-xl border border-sand bg-ivory/40 p-5 text-left text-sm">
                <div className="flex justify-between border-b border-sand pb-3">
                  <div>
                    <span className="text-xs text-charcoal-soft">Booking Reference</span>
                    <p className="font-mono text-xl font-extrabold text-forest">
                      {confirmed.booking_reference}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-charcoal-soft">Status</span>
                    <p className="font-bold text-terracotta">{confirmed.status.replace(/_/g, " ")}</p>
                  </div>
                </div>

                <div className="mt-4">
                  <span className="text-xs font-bold uppercase tracking-wider text-charcoal-soft">
                    Trip Summary
                  </span>
                  <div className="mt-2 space-y-2">
                    <div className="flex justify-between rounded bg-white p-2.5 text-xs">
                      <span className="text-charcoal-soft">Cab Type</span>
                      <span className="font-semibold text-forest">
                        {confirmed.cab_type} &bull; {TRIP_TYPE_LABELS[confirmed.trip_type]}
                      </span>
                    </div>
                    <div className="flex justify-between rounded bg-white p-2.5 text-xs">
                      <span className="text-charcoal-soft">Route</span>
                      <span className="font-semibold text-forest">
                        {confirmed.pickup_location} &rarr; {confirmed.drop_location}
                      </span>
                    </div>
                    <div className="flex justify-between rounded bg-white p-2.5 text-xs">
                      <span className="text-charcoal-soft">Pickup</span>
                      <span className="font-semibold text-forest">
                        {confirmed.pickup_date} at {confirmed.pickup_time}
                      </span>
                    </div>
                    <div className="flex justify-between rounded bg-white p-2.5 text-xs">
                      <span className="text-charcoal-soft">Passengers</span>
                      <span className="font-semibold text-forest">{confirmed.passengers}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 rounded-lg bg-sand/30 p-3.5 text-xs">
                  <div className="flex justify-between py-1 text-charcoal-soft">
                    <span>Fare</span>
                    <span className="font-bold text-terracotta">
                      To be confirmed by our team
                    </span>
                  </div>
                </div>
                <p className="mt-3 text-[11px] leading-relaxed text-charcoal-soft">
                  We will share a final quote for this trip — subject to route,
                  traffic and vehicle availability — before dispatch.
                </p>
              </div>

              <div className="mt-6 flex justify-center gap-4">
                <Button href="/cabs" onClick={reset} variant="primary">
                  Book Another Cab
                </Button>
              </div>
            </div>
          </div>
        ) : (
          /* Booking form */
          <div className="grid gap-8 lg:grid-cols-[1fr_360px]">
            <form
              onSubmit={handleSubmit}
              className="space-y-6 rounded-2xl bg-white p-5 shadow-xl ring-1 ring-black/5 sm:p-8"
            >
              {error && (
                <div className="rounded-lg bg-red-50 p-3 text-sm font-semibold text-red-700">
                  {error}
                </div>
              )}

              {/* Trip type */}
              <fieldset>
                <legend className={labelClasses}>Trip Type</legend>
                <div className="mt-3 grid gap-3 sm:grid-cols-3">
                  {(Object.keys(TRIP_TYPE_LABELS) as CabTripType[]).map((key) => (
                    <button
                      key={key}
                      type="button"
                      onClick={() => setTripType(key)}
                      aria-pressed={tripType === key}
                      className={`rounded-xl border px-4 py-3 text-left text-sm font-semibold transition-colors ${
                        tripType === key
                          ? "border-terracotta bg-terracotta/5 text-forest"
                          : "border-line bg-cream text-charcoal-soft hover:border-terracotta/40"
                      }`}
                    >
                      {TRIP_TYPE_LABELS[key]}
                    </button>
                  ))}
                </div>
              </fieldset>

              {/* Cab type */}
              <div>
                <label htmlFor="cabType" className={labelClasses}>
                  Cab Type / Vehicle Preference
                </label>
                <input
                  id="cabType"
                  type="text"
                  required
                  value={cabType}
                  onChange={(e) => setCabType(e.target.value)}
                  placeholder="e.g. Sedan, SUV, Innova, Tempo Traveller"
                  className={`${fieldClasses} mt-2`}
                />
              </div>

              {/* Route + schedule */}
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label htmlFor="pickupLocation" className={labelClasses}>
                    Pickup Location
                  </label>
                  <input
                    id="pickupLocation"
                    type="text"
                    required
                    value={pickupLocation}
                    onChange={(e) => setPickupLocation(e.target.value)}
                    placeholder="Hotel, airport or address"
                    className={`${fieldClasses} mt-2`}
                  />
                </div>
                <div>
                  <label htmlFor="dropLocation" className={labelClasses}>
                    Drop Location
                  </label>
                  <input
                    id="dropLocation"
                    type="text"
                    required
                    value={dropLocation}
                    onChange={(e) => setDropLocation(e.target.value)}
                    placeholder="Destination address"
                    className={`${fieldClasses} mt-2`}
                  />
                </div>
                <div>
                  <label htmlFor="pickupDate" className={labelClasses}>
                    Pickup Date
                  </label>
                  <input
                    id="pickupDate"
                    type="date"
                    required
                    min={tomorrowStr()}
                    value={pickupDate}
                    onChange={(e) => setPickupDate(e.target.value)}
                    className={`${fieldClasses} mt-2`}
                  />
                </div>
                <div>
                  <label htmlFor="pickupTime" className={labelClasses}>
                    Pickup Time
                  </label>
                  <input
                    id="pickupTime"
                    type="time"
                    required
                    value={pickupTime}
                    onChange={(e) => setPickupTime(e.target.value)}
                    className={`${fieldClasses} mt-2`}
                  />
                </div>
                <div>
                  <label htmlFor="distanceKms" className={labelClasses}>
                    Approx. Distance (km)
                  </label>
                  <input
                    id="distanceKms"
                    type="number"
                    min={0}
                    step="0.5"
                    value={distanceKms}
                    onChange={(e) => setDistanceKms(e.target.value)}
                    placeholder="e.g. 25"
                    className={`${fieldClasses} mt-2`}
                  />
                  <p className="mt-1 text-[11px] text-charcoal-soft/70">
                    Helps us provide an accurate quote. Overland estimates are welcome.
                  </p>
                </div>
                <div>
                  <label htmlFor="passengers" className={labelClasses}>
                    Passengers
                  </label>
                  <select
                    id="passengers"
                    value={passengers}
                    onChange={(e) => setPassengers(Number(e.target.value))}
                    className={`${fieldClasses} mt-2`}
                  >
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((n) => (
                      <option key={n} value={n}>
                        {n} {n === 1 ? "Passenger" : "Passengers"}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Contact */}
              <fieldset className="rounded-xl border border-line bg-ivory/40 p-4 sm:p-5">
                <legend className={labelClasses}>Your Contact Details</legend>
                <div className="mt-3 grid gap-4 sm:grid-cols-3">
                  <div>
                    <label htmlFor="fullName" className="sr-only">
                      Full Name
                    </label>
                    <input
                      id="fullName"
                      type="text"
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Full Name"
                      className={fieldClasses}
                    />
                  </div>
                  <div>
                    <label htmlFor="email" className="sr-only">
                      Email
                    </label>
                    <input
                      id="email"
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Email Address"
                      className={fieldClasses}
                    />
                  </div>
                  <div>
                    <label htmlFor="phone" className="sr-only">
                      Phone
                    </label>
                    <input
                      id="phone"
                      type="tel"
                      required
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="Phone Number"
                      className={fieldClasses}
                    />
                  </div>
                </div>
              </fieldset>

              {/* Special requirements */}
              <div>
                <label htmlFor="specialRequirements" className={labelClasses}>
                  Special Requirements (optional)
                </label>
                <textarea
                  id="specialRequirements"
                  rows={3}
                  value={specialRequirements}
                  onChange={(e) => setSpecialRequirements(e.target.value)}
                  placeholder="Child seat, extra luggage, stopovers, AC preference, etc."
                  className={`${fieldClasses} mt-2`}
                />
              </div>

              <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
                <p className="text-xs text-charcoal-soft">
                  Fare:{" "}
                  <span className="text-base font-extrabold text-terracotta">
                    Price on request
                  </span>
                </p>
                <Button type="submit" variant="secondary" disabled={isSubmitting}>
                  {isSubmitting ? "Sending Request..." : "Request This Cab"}
                </Button>
              </div>
            </form>

            {/* Price summary sidebar */}
            <aside className="h-fit space-y-5">
              <div className="rounded-2xl bg-white p-6 shadow-xl ring-1 ring-black/5">
                <h3 className="font-display text-lg font-bold text-forest">Fare</h3>
                <div className="mt-4 space-y-2 text-sm">
                  <div className="flex justify-between text-charcoal-soft">
                    <span>Your trip ({distance} km)</span>
                    <span className="font-extrabold text-terracotta">Price on request</span>
                  </div>
                </div>
                <p className="mt-3 text-[11px] leading-relaxed text-charcoal-soft">
                  We do not charge a published rate. Our team shares a confirmed
                  quote for your route before the trip — no advance payment
                  required to place the request.
                </p>
              </div>

              <div className="rounded-2xl border border-line bg-ivory p-6">
                <h3 className="font-display text-base font-bold text-forest">Why book with us?</h3>
                <ul className="mt-4 space-y-3 text-sm text-charcoal-soft">
                  {[
                    "Clean, verified & sanitised cabs",
                    "All-India airport pickups & outstation trips",
                    "Immediate email confirmation to our team",
                    "Flexible booking — no advance payment needed",
                  ].map((item) => (
                    <li key={item} className="flex items-start gap-2.5">
                      <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-forest text-[10px] font-bold text-ivory">
                        ✓
                      </span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              <p className="px-2 text-xs leading-relaxed text-charcoal-soft/80">
                Prefer to talk to us? Call or WhatsApp{" "}
                <a
                  href="tel:+918940185116"
                  className="font-semibold text-terracotta hover:underline"
                >
                  +91 89401 85116
                </a>{" "}
                or email{" "}
                <a
                  href="mailto:infoexplorerschoice@gmail.com"
                  className="font-semibold text-terracotta hover:underline"
                >
                  infoexplorerschoice@gmail.com
                </a>
                .
              </p>
            </aside>
          </div>
        )}

        <div className="mt-14">
          <p className="text-center text-sm text-charcoal-soft">
            Want to re-check a past request?{" "}
            <Link href="/contact" className="font-semibold text-terracotta hover:underline">
              Contact our team
            </Link>{" "}
            with your booking reference.
          </p>
        </div>
      </Container>
    </div>
  );
}