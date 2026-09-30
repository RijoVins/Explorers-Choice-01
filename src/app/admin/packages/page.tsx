"use client";

import { useEffect, useState, useCallback } from "react";
import { adminApi, formatMoneyAmount, packageImageUrl, uploadPackageImage, type Package, type DestinationOption } from "@/lib/admin";
import { useAuth } from "@/components/providers";
import { ItineraryEditor } from "./ItineraryEditor";
import { imageUrlError } from "@/lib/images";
import { CLIENT_API_URL as API_URL } from "@/lib/api";

const toLines = (list: string[] | undefined): string[] => (list ?? []).filter((s) => s.trim());

const EMPTY_FORM = {
  destination_id: "",
  name: "",
  slug: "",
  short_description: "",
  description: "",
  duration_days: "",
  duration_nights: "",
  starting_price: "",
  currency: "USD",
  hero_image: "",
  gallery: Array.from({ length: 6 }, () => ""),
  highlights: [] as string[],
  included: [] as string[],
  excluded: [] as string[],
  accommodation_summary: "",
  transportation_summary: "",
  meal_summary: "",
  cancellation_policy: "",
  important_information: [] as string[],
  booking_mode: "REQUEST_ONLY" as "REQUEST_ONLY" | "INSTANT_BOOKING",
  is_featured: false,
  is_active: true,
};

function slugify(input: string): string {
  return input
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 220);
}

const INPUT_CLS =
  "mt-2 w-full rounded-xl border border-line bg-white px-4 py-2.5 text-sm text-charcoal placeholder:text-charcoal-soft/60 focus:border-terracotta focus:outline-none";

const LABEL_CLS = "block text-sm font-semibold text-forest";

const listToText = (list: string[]): string => list.join("\n");
const textToList = (text: string): string[] =>
  text.split("\n").map((s) => s.trim()).filter((s) => s.length > 0);

export default function AdminPackagesPage() {
  const [packages, setPackages] = useState<Package[]>([]);
  const [destinations, setDestinations] = useState<DestinationOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [flash, setFlash] = useState("");

  const [editingId, setEditingId] = useState<number | null>(null);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [uploading, setUploading] = useState(false);

  const { user } = useAuth();
  const editingPackage = editingId !== null
    ? packages.find((p) => p.id === editingId) ?? null
    : null;

  const load = useCallback(() => {
    adminApi
      .packages()
      .then(setPackages)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load packages."))
      .finally(() => setLoading(false));
  }, []);

  useEffect(load, [load]);

  useEffect(() => {
    adminApi
      .destinations()
      .then(setDestinations)
      .catch(() => setDestinations([]));
  }, []);

  function startCreate() {
    setCreating(true);
    setEditingId(null);
    setForm(EMPTY_FORM);
    setFlash("");
  }

  function startEdit(p: Package) {
    setCreating(false);
    setEditingId(p.id);
    setForm({
      destination_id: String(p.destination_id),
      name: p.name,
      slug: p.slug,
      short_description: p.short_description,
      description: p.description,
      duration_days: String(p.duration_days),
      duration_nights: String(p.duration_nights),
      starting_price: String(p.starting_price),
      currency: p.currency,
      hero_image: p.hero_image,
      gallery: Array.from({ length: 6 }, (_, i) => p.gallery?.[i] ?? ""),
      highlights: toLines(p.highlights),
      included: toLines(p.included),
      excluded: toLines(p.excluded),
      accommodation_summary: p.accommodation_summary,
      transportation_summary: p.transportation_summary,
      meal_summary: p.meal_summary,
      cancellation_policy: p.cancellation_policy,
      important_information: toLines(p.important_information),
      booking_mode: p.booking_mode,
      is_featured: p.is_featured,
      is_active: p.is_active,
    });
    setFlash("");
  }

  async function handleImageUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setFlash("");
    setUploading(true);
    try {
      const { url } = await uploadPackageImage(file);
      setForm((f) => ({ ...f, hero_image: url }));
    } catch (err) {
      setFlash(err instanceof Error ? err.message : "Could not upload the image.");
    } finally {
      setUploading(false);
    }
  }

  async function save() {
    setFlash("");
    // BUG-16: reject image URLs that next/image would refuse to render.
    const heroError = imageUrlError(form.hero_image, [API_URL]);
    const galleryError = form.gallery.map((g) => imageUrlError(g, [API_URL])).find(Boolean) ?? "";
    if (heroError || galleryError) {
      setFlash(heroError || galleryError);
      return;
    }
    const payload = {
      destination_id: Number(form.destination_id),
      name: form.name.trim(),
      slug: (form.slug.trim() || slugify(form.name.trim())),
      short_description: form.short_description.trim(),
      description: form.description.trim(),
      duration_days: Number(form.duration_days) || 0,
      duration_nights: Number(form.duration_nights) || 0,
      starting_price: Number(form.starting_price) || 0,
      currency: (form.currency.trim() || "USD").toUpperCase().slice(0, 3),
      hero_image: form.hero_image,
      gallery: form.gallery.map((g) => g.trim()).filter((g) => g.length > 0),
      highlights: textToList(form.highlights.join("\n")),
      included: textToList(form.included.join("\n")),
      excluded: textToList(form.excluded.join("\n")),
      accommodation_summary: form.accommodation_summary.trim(),
      transportation_summary: form.transportation_summary.trim(),
      meal_summary: form.meal_summary.trim(),
      cancellation_policy: form.cancellation_policy.trim(),
      important_information: textToList(form.important_information.join("\n")),
      booking_mode: form.booking_mode,
      is_featured: form.is_featured,
      is_active: form.is_active,
    };
    if (!payload.name || !payload.destination_id) {
      setFlash("Give the package a name and choose a destination.");
      return;
    }
    if (!payload.slug) {
      setFlash("Give the package a slug.");
      return;
    }
    try {
      if (editingId !== null) await adminApi.updatePackage(editingId, payload);
      else await adminApi.createPackage(payload);
      setCreating(false);
      setEditingId(null);
      setFlash(editingId !== null ? "Package updated." : "Package created.");
      load();
    } catch (err) {
      setFlash(err instanceof Error ? err.message : "Could not save the package.");
    }
  }

  async function remove(p: Package) {
    setFlash("");
    if (!confirm(`Delete the package "${p.name}"?`)) return;
    try {
      await adminApi.deletePackage(p.id);
      setFlash("Package deleted.");
      load();
    } catch (err) {
      setFlash(err instanceof Error ? err.message : "Could not delete the package.");
    }
  }

  async function toggleActive(p: Package) {
    setFlash("");
    try {
      await adminApi.updatePackage(p.id, { is_active: !p.is_active });
      load();
    } catch (err) {
      setFlash(err instanceof Error ? err.message : "Could not update the package.");
    }
  }

  if (error && packages.length === 0) return <p className="rounded-xl border border-terracotta/30 bg-terracotta/10 p-4 text-sm text-charcoal">{error}</p>;
  if (loading) return <p className="text-charcoal-soft">Loading packages…</p>;

  const open = creating || editingId !== null;

  return (
    <>
      <section className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-6 sm:mb-8 sm:border-0 sm:pb-0">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Catalogue</p>
          <h1 className="mt-2 font-display text-4xl leading-tight text-forest sm:text-5xl">Packages</h1>
          <p className="mt-3 max-w-2xl text-charcoal-soft">Curated itineraries sold on the site. Upload a hero image and fill in the details.</p>
        </div>
        {!open && (
          <button type="button" onClick={startCreate} className="rounded-full bg-terracotta px-6 py-2.5 text-sm font-semibold text-ivory transition-colors hover:bg-terracotta-dark">
            New package
          </button>
        )}
      </section>

      {flash && <p role="alert" className="mt-6 rounded-xl border border-forest/25 bg-forest/5 p-4 text-sm text-forest">{flash}</p>}

      {open && (
        <section className="mt-6 rounded-2xl border border-line bg-cream p-6">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">{creating ? "Create a package" : "Edit package"}</p>

          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <label className={LABEL_CLS}>
              Package name *
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value, slug: (form.slug || form.name === "" ? slugify(e.target.value) : form.slug) })} placeholder="e.g. Royal Rajasthan with Varanasi" className={INPUT_CLS} />
            </label>
            <label className={LABEL_CLS}>
              Slug
              <input value={form.slug} onChange={(e) => setForm({ ...form, slug: e.target.value })} placeholder="e.g. royal-rajasthan-varanasi" className={INPUT_CLS} />
            </label>
            <label className={LABEL_CLS}>
              Destination *
              <select value={form.destination_id} onChange={(e) => setForm({ ...form, destination_id: e.target.value })} className={INPUT_CLS}>
                <option value="">Choose a destination</option>
                {destinations.map((d) => <option key={d.id} value={d.id}>{d.name}{d.country ? ` · ${d.country}` : ""}</option>)}
              </select>
            </label>
            <label className={LABEL_CLS}>
              Duration (days)
              <input type="number" min={0} value={form.duration_days} onChange={(e) => setForm({ ...form, duration_days: e.target.value })} placeholder="e.g. 9" className={INPUT_CLS} />
            </label>
            <label className={LABEL_CLS}>
              Duration (nights)
              <input type="number" min={0} value={form.duration_nights} onChange={(e) => setForm({ ...form, duration_nights: e.target.value })} placeholder="e.g. 8" className={INPUT_CLS} />
            </label>
            <div className="grid grid-cols-2 gap-2">
              <label className={LABEL_CLS}>
                From price
                <input type="number" min={0} step="0.01" value={form.starting_price} onChange={(e) => setForm({ ...form, starting_price: e.target.value })} placeholder="e.g. 45000" className={INPUT_CLS} />
              </label>
              <label className={LABEL_CLS}>
                Currency
                <input maxLength={3} value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })} placeholder="INR" className={INPUT_CLS} />
              </label>
            </div>
            <label className={LABEL_CLS}>
              Booking mode
              <select value={form.booking_mode} onChange={(e) => setForm({ ...form, booking_mode: e.target.value as "REQUEST_ONLY" | "INSTANT_BOOKING" })} className={INPUT_CLS}>
                <option value="REQUEST_ONLY">Request only</option>
                <option value="INSTANT_BOOKING">Instant booking</option>
              </select>
            </label>
            <label className={LABEL_CLS}>
              Short description
              <input value={form.short_description} onChange={(e) => setForm({ ...form, short_description: e.target.value })} placeholder="One-line teaser for cards" className={INPUT_CLS} />
            </label>
            <label className={`${LABEL_CLS} sm:col-span-2`}>
              Description
              <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={4} placeholder="Full narrative of the journey…" className={`${INPUT_CLS} min-h-28`} />
            </label>
            <label className={LABEL_CLS}>
              Accommodation
              <textarea value={form.accommodation_summary} onChange={(e) => setForm({ ...form, accommodation_summary: e.target.value })} rows={2} placeholder="e.g. Heritage hotels and boutique stays" className={`${INPUT_CLS} min-h-16`} />
            </label>
            <label className={LABEL_CLS}>
              Transportation
              <textarea value={form.transportation_summary} onChange={(e) => setForm({ ...form, transportation_summary: e.target.value })} rows={2} placeholder="e.g. Private AC vehicle with driver" className={`${INPUT_CLS} min-h-16`} />
            </label>
            <label className={LABEL_CLS}>
              Meals
              <textarea value={form.meal_summary} onChange={(e) => setForm({ ...form, meal_summary: e.target.value })} rows={2} placeholder="e.g. Daily breakfast; some dinners included" className={`${INPUT_CLS} min-h-16`} />
            </label>
            <label className={LABEL_CLS}>
              Cancellation policy
              <textarea value={form.cancellation_policy} onChange={(e) => setForm({ ...form, cancellation_policy: e.target.value })} rows={2} placeholder="e.g. Free cancellation up to 30 days before departure" className={`${INPUT_CLS} min-h-16`} />
            </label>
            <label className={LABEL_CLS}>
              Highlights (one per line)
              <textarea value={listToText(form.highlights)} onChange={(e) => setForm({ ...form, highlights: textToList(e.target.value) })} rows={4} placeholder={"Taj Mahal at sunrise\nSand dunes of Jaisalmer"} className={`${INPUT_CLS} min-h-24`} />
            </label>
            <label className={LABEL_CLS}>
              Included (one per line)
              <textarea value={listToText(form.included)} onChange={(e) => setForm({ ...form, included: textToList(e.target.value) })} rows={4} placeholder={"Airport transfers\nAccommodation with breakfast"} className={`${INPUT_CLS} min-h-24`} />
            </label>
            <label className={LABEL_CLS}>
              Excluded (one per line)
              <textarea value={listToText(form.excluded)} onChange={(e) => setForm({ ...form, excluded: textToList(e.target.value) })} rows={4} placeholder={"International flights\nTravel insurance"} className={`${INPUT_CLS} min-h-24`} />
            </label>
            <label className={`${LABEL_CLS} lg:col-span-2`}>
              Important information (one per line)
              <textarea value={listToText(form.important_information)} onChange={(e) => setForm({ ...form, important_information: textToList(e.target.value) })} rows={3} placeholder={"Carry comfortable walking shoes\nPassport required for border areas"} className={`${INPUT_CLS} min-h-16`} />
            </label>
            <label className={LABEL_CLS}>
              Gallery image URL {1}
              <input value={form.gallery[0]} onChange={(e) => setForm({ ...form, gallery: [e.target.value, ...form.gallery.slice(1)] })} placeholder="https://…" className={INPUT_CLS} />
            </label>
            <label className={LABEL_CLS}>
              Gallery image URL {2}
              <input value={form.gallery[1]} onChange={(e) => setForm({ ...form, gallery: [form.gallery[0], e.target.value, ...form.gallery.slice(2)] })} placeholder="https://…" className={INPUT_CLS} />
            </label>
            <label className={LABEL_CLS}>
              Gallery image URL {3}
              <input value={form.gallery[2]} onChange={(e) => setForm({ ...form, gallery: [...form.gallery.slice(0, 2), e.target.value, ...form.gallery.slice(3)] })} placeholder="https://…" className={INPUT_CLS} />
            </label>
            <label className={LABEL_CLS}>
              Gallery image URL {4}
              <input value={form.gallery[3]} onChange={(e) => setForm({ ...form, gallery: [...form.gallery.slice(0, 3), e.target.value, ...form.gallery.slice(4)] })} placeholder="https://…" className={INPUT_CLS} />
            </label>
            <label className={LABEL_CLS}>
              Gallery image URL {5}
              <input value={form.gallery[4]} onChange={(e) => setForm({ ...form, gallery: [...form.gallery.slice(0, 4), e.target.value, ...form.gallery.slice(5)] })} placeholder="https://…" className={INPUT_CLS} />
            </label>
            <label className={LABEL_CLS}>
              Gallery image URL {6}
              <input value={form.gallery[5]} onChange={(e) => setForm({ ...form, gallery: [...form.gallery.slice(0, 5), e.target.value] })} placeholder="https://…" className={INPUT_CLS} />
            </label>
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-line bg-white p-5">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Hero image</p>
              <p className="mt-1 text-xs text-charcoal-soft">Upload a photo to feature as the package cover. JPEG, PNG, WebP or GIF up to 10&nbsp;MB.</p>
              {form.hero_image ? (
                <div className="mt-3 overflow-hidden rounded-xl border border-line">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={packageImageUrl(form.hero_image)} alt="Package preview" className="h-48 w-full object-cover" />
                </div>
              ) : (
                <div className="mt-3 flex h-48 items-center justify-center rounded-xl border border-dashed border-line bg-ivory text-sm text-charcoal-soft">
                  No image uploaded yet
                </div>
              )}
              <label className={`mt-3 inline-flex cursor-pointer items-center gap-2 rounded-full border border-forest/30 px-5 py-2 text-sm font-semibold text-forest transition-colors hover:bg-forest hover:text-ivory ${uploading ? "opacity-60" : ""}`}>
                {uploading ? "Uploading…" : form.hero_image ? "Replace image" : "Upload image"}
                <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" className="hidden" onChange={handleImageUpload} disabled={uploading} />
              </label>
              {form.hero_image && (
                <button type="button" onClick={() => setForm({ ...form, hero_image: "" })} className="mt-2 block text-sm font-semibold text-terracotta hover:underline">
                  Remove image
                </button>
              )}
            </div>

            <div className="flex flex-col items-start gap-4 rounded-2xl border border-line bg-white p-5">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">Publishing</p>
              <label className="flex items-center gap-2 text-sm font-semibold text-forest">
                <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} className="h-4 w-4 accent-terracotta" />
                Visible on the site
              </label>
              <label className="flex items-center gap-2 text-sm font-semibold text-forest">
                <input type="checkbox" checked={form.is_featured} onChange={(e) => setForm({ ...form, is_featured: e.target.checked })} className="h-4 w-4 accent-terracotta" />
                Featured on the homepage
              </label>
              <div className="mt-auto w-full rounded-xl bg-ivory px-4 py-3 text-xs text-charcoal-soft">
                Price shown on the site: <span className="font-semibold text-forest">{formatMoneyAmount(Number(form.starting_price) || 0, form.currency.trim() || "USD")} per person (starting from).</span>
              </div>
            </div>
          </div>

          <div className="mt-6 flex gap-3">
            <button type="button" onClick={save} className="rounded-full bg-forest px-6 py-2.5 text-sm font-semibold text-ivory transition-colors hover:bg-forest-dark">
              {editingId !== null ? "Save package" : "Create package"}
            </button>
            <button type="button" onClick={() => { setCreating(false); setEditingId(null); }} className="rounded-full border border-line bg-white px-6 py-2.5 text-sm font-semibold text-charcoal-soft hover:text-forest">
              Cancel
            </button>
          </div>

          {/* Itinerary — needs an existing package id, so it only appears while editing. */}
          {editingPackage && (
            <div className="mt-8">
              <ItineraryEditor
                packageId={editingPackage.id}
                days={Array.isArray(editingPackage.itinerary) ? (editingPackage.itinerary as unknown as { id?: number; day_number: number; title: string; description: string; activities: string[]; meals: string; accommodation: string; transportation: string }[]) : []}
                userRole={user?.role}
              />
            </div>
          )}
        </section>
      )}

      {packages.length === 0 ? (
        <div className="mt-8 rounded-2xl border border-line bg-cream p-10 text-center">
          <p className="font-display text-2xl text-forest">No packages yet.</p>
          <p className="mt-2 text-sm text-charcoal-soft">Create your first itinerary and it will show up on the packages page.</p>
        </div>
      ) : (
        <div className="mt-8 space-y-3">
          {packages.map((p) => (
            <div key={p.id} className="flex flex-col gap-4 rounded-2xl border border-line bg-cream p-5 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex min-w-0 items-center gap-4">
                {p.hero_image ? (
                  <div className="hidden h-16 w-24 shrink-0 overflow-hidden rounded-xl border border-line sm:block">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={packageImageUrl(p.hero_image)} alt={p.name} className="h-full w-full object-cover" />
                  </div>
                ) : (
                  <div className="hidden h-16 w-24 shrink-0 items-center justify-center rounded-xl border border-dashed border-line bg-white text-[11px] text-charcoal-soft sm:flex">No image</div>
                )}
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="font-semibold text-forest">{p.name}</p>
                    {p.is_featured && <span className="rounded-full bg-terracotta/15 px-2.5 py-0.5 text-[11px] font-semibold text-terracotta">featured</span>}
                    {!p.is_active && <span className="rounded-full bg-sand-light px-2.5 py-0.5 text-[11px] font-semibold text-charcoal-soft">archived</span>}
                    {p.booking_mode === "INSTANT_BOOKING" && <span className="rounded-full bg-ivory px-2.5 py-0.5 text-[11px] font-semibold text-forest">instant</span>}
                  </div>
                  <p className="mt-0.5 line-clamp-1 text-sm text-charcoal-soft">
                    {p.destination?.name ?? `Destination #${p.destination_id}`} · {p.duration_days ? `${p.duration_days}d` : ""}{p.duration_nights ? `/${p.duration_nights}n` : ""} · from {formatMoneyAmount(p.starting_price, p.currency)}
                  </p>
                </div>
              </div>
              <div className="flex shrink-0 gap-3">
                <button type="button" onClick={() => toggleActive(p)} className="rounded-full border border-forest/30 px-5 py-2 text-sm font-semibold text-forest transition-colors hover:bg-forest hover:text-ivory">
                  {p.is_active ? "Archive" : "Restore"}
                </button>
                <button type="button" onClick={() => startEdit(p)} className="rounded-full border border-forest/30 px-5 py-2 text-sm font-semibold text-forest transition-colors hover:bg-forest hover:text-ivory">Edit</button>
                <button type="button" onClick={() => remove(p)} className="rounded-full border border-terracotta/30 px-5 py-2 text-sm font-semibold text-terracotta transition-colors hover:bg-terracotta hover:text-ivory">Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}