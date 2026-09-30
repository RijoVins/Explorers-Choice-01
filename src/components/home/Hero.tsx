"use client";

import Image from "next/image";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Container } from "@/components/ui/Container";

export function Hero() {
  const router = useRouter();
  const [mode, setMode] = useState("Holidays");
  const [tripType, setTripType] = useState("Round trip");
  const [travellers, setTravellers] = useState("2 Adults, 1 Room");

  function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const destination = String(formData.get("destination") ?? "");

    if (mode === "Holidays") {
      router.push(`/packages${destination ? `?destination=${encodeURIComponent(destination)}` : ""}`);
    } else if (mode === "Hotels") {
      router.push(`/hotels${destination ? `?search=${encodeURIComponent(destination)}` : ""}`);
    } else if (mode === "Cabs") {
      router.push(`/cabs`);
    } else {
      router.push(`/contact?subject=${encodeURIComponent(`${mode} enquiry`)}`);
    }
  }

  return (
    <section className="relative overflow-hidden">
      <div className="relative min-h-[720px] w-full pb-14 pt-14 sm:min-h-[700px] sm:pb-20 sm:pt-20">
        <Image
          src="https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=2000&q=80"
          alt="Snow-capped Himalayan peaks glowing at golden hour"
          fill
          priority
          sizes="100vw"
          className="object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-dark/70 via-forest-dark/20 to-transparent" />

        <Container className="relative z-10">
          <div className="mx-auto max-w-4xl text-center">
            <p className="mb-4 text-xs font-bold uppercase tracking-[0.28em] text-ivory/85">
              Explorers Choice · Travel made personal
            </p>
            <h1 className="font-display text-5xl leading-[1.05] text-ivory sm:text-6xl lg:text-7xl">
              Find your next way out.
            </h1>
            <p className="mx-auto mt-5 max-w-2xl text-base leading-relaxed text-ivory/90 sm:text-lg">
              Compare stays, discover considered itineraries, and let the details fall into place.
            </p>
          </div>

          <div className="mx-auto mt-10 max-w-5xl overflow-hidden rounded-2xl bg-ivory shadow-2xl shadow-forest-dark/30">
            <div className="flex border-b border-line px-2 sm:overflow-x-auto sm:px-6" role="tablist" aria-label="Travel products">
              {[ "Flights", "Hotels", "Holidays", "Trains", "Cabs"].map((item) => (
                <button
                  key={item}
                  type="button"
                  role="tab"
                  aria-selected={mode === item}
                  onClick={() => setMode(item)}
                  className={`relative min-w-0 flex-1 px-2 py-4 text-xs font-bold transition-colors sm:flex-none sm:px-6 sm:text-sm ${mode === item ? "text-forest" : "text-charcoal-soft hover:text-forest"}`}
                >
                  {item}
                  {mode === item && <span className="absolute inset-x-4 bottom-0 h-1 rounded-t-full bg-terracotta sm:inset-x-6" />}
                </button>
              ))}
            </div>

            <form onSubmit={handleSearch} className="p-4 sm:p-6">
              <div className="mb-5 flex flex-wrap items-center gap-x-6 gap-y-3 text-sm text-charcoal-soft">
                {mode === "Flights" && ["Round trip", "One way", "Multi-city"].map((item) => (
                  <label key={item} className="inline-flex items-center gap-2 font-semibold">
                    <input type="radio" name="tripType" value={item} checked={tripType === item} onChange={() => setTripType(item)} className="accent-terracotta" />
                    {item}
                  </label>
                ))}
                {mode !== "Flights" && <span className="text-xs font-semibold text-forest sm:text-sm">{mode === "Holidays" ? "Curated journeys for every kind of explorer" : mode === "Cabs" ? "Airport transfers, city rides & outstation cabs" : "Handpicked stays, ready when you are"}</span>}
              </div>

              <div className="grid gap-3 md:grid-cols-[1.4fr_1fr_1fr_auto]">
                <label className="flex min-h-16 flex-col justify-center rounded-xl border border-line bg-cream px-4 py-2 text-left focus-within:border-terracotta">
                  <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-charcoal-soft">{mode === "Flights" ? "From / To" : "Where do you want to go?"}</span>
                  <input name="destination" required={mode !== "Trains" && mode !== "Cabs"} placeholder={mode === "Flights" ? "Delhi, Mumbai or abroad" : mode === "Cabs" ? "Pickup location" : "Search a destination"} className="mt-1 w-full bg-transparent text-sm font-semibold text-charcoal outline-none placeholder:text-charcoal-soft/60" />
                </label>
                <label className="flex min-h-16 flex-col justify-center rounded-xl border border-line bg-cream px-4 py-2 text-left focus-within:border-terracotta">
                  <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-charcoal-soft">Check in</span>
                  <input name="checkIn" type="date" className="mt-1 w-full bg-transparent text-sm font-semibold text-charcoal outline-none" />
                </label>
                <label className="flex min-h-16 flex-col justify-center rounded-xl border border-line bg-cream px-4 py-2 text-left focus-within:border-terracotta">
                  <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-charcoal-soft">Guests</span>
                  <select name="travellers" value={travellers} onChange={(event) => setTravellers(event.target.value)} className="mt-1 w-full bg-transparent text-sm font-semibold text-charcoal outline-none">
                    <option>1 Adult, 1 Room</option>
                    <option>2 Adults, 1 Room</option>
                    <option>2 Adults, 2 Rooms</option>
                    <option>Family · 2 Adults, 2 Children</option>
                  </select>
                </label>
                <button type="submit" className="min-h-16 rounded-xl bg-terracotta px-7 text-sm font-bold text-ivory transition-colors hover:bg-terracotta-dark focus-visible:outline-terracotta">
                  Search
                </button>
              </div>
              <p className="mt-4 text-xs text-charcoal-soft">No hidden fees · Flexible planning · Local expertise</p>
            </form>
          </div>

          <div className="mx-auto mt-5 flex max-w-5xl flex-wrap justify-center gap-2 text-xs font-semibold text-ivory/90 sm:justify-start">
            {["Popular: Rajasthan", "Kerala backwaters", "Ladakh", "Goa beaches"].map((item) => (
              <span key={item} className="rounded-full border border-ivory/30 bg-forest-dark/20 px-3 py-1.5 backdrop-blur-sm">{item}</span>
            ))}
          </div>
        </Container>
      </div>
    </section>
  );
}
