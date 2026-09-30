"use client";

import { useMemo, useState } from "react";
import { adminApi, type ItineraryDayInput } from "@/lib/admin";
import { isStaffRole } from "@/lib/auth";

const ITINERARY_ROLES = new Set(["MANAGER", "ADMIN"]);

type ApiDay = {
  id?: number;
  day_number: number;
  title: string;
  description: string;
  activities: string[];
  meals: string;
  accommodation: string;
  transportation: string;
};

const blank = (dayNumber: number): ItineraryDayInput => ({
  day_number: dayNumber,
  title: "",
  description: "",
  activities: [],
  meals: "",
  accommodation: "",
  transportation: "",
});

/** The itinerary endpoints require MANAGER or ADMIN, so the editor is read-only
 * (or hidden for "New package") for lower roles while still showing real data. */
export function ItineraryEditor({
  packageId,
  days,
  userRole,
}: {
  packageId: number;
  days: ApiDay[];
  userRole?: string | null;
}) {
  const initial = useMemo<ItineraryDayInput[]>(
    () =>
      [...days]
        .sort((a, b) => a.day_number - b.day_number)
        .map((d) => ({
          day_number: d.day_number,
          title: d.title ?? "",
          description: d.description ?? "",
          activities: Array.isArray(d.activities) ? d.activities.map(String) : [],
          meals: d.meals ?? "",
          accommodation: d.accommodation ?? "",
          transportation: d.transportation ?? "",
        })),
    [days],
  );

  const [rows, setRows] = useState<ItineraryDayInput[]>(initial);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  const canEdit = isStaffRole(userRole) && ITINERARY_ROLES.has(userRole ?? "");

  const update = (index: number, patch: Partial<ItineraryDayInput>) => {
    setSaved(false);
    setRows((prev) => prev.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  };

  const addRow = () => {
    setSaved(false);
    setRows((prev) => {
      const next = [...prev];
      next.push(blank((next[next.length - 1]?.day_number ?? 0) + 1));
      return next;
    });
  };

  const removeRow = (index: number) => {
    setSaved(false);
    setRows((prev) => prev.filter((_, i) => i !== index));
  };

  const renumber = () =>
    setRows((prev) => prev.map((row, i) => ({ ...row, day_number: i + 1 })));

  const save = async () => {
    setError("");
    setSaved(false);
    setSaving(true);
    try {
      const ordered = rows
        .map((row, i) => ({ ...row, day_number: i + 1 }))
        .filter((row) => row.title.trim() || row.description.trim());
      await adminApi.replaceItinerary(packageId, ordered);
      setSaving(false);
      setSaved(true);
    } catch (err) {
      setSaving(false);
      setError(err instanceof Error ? err.message : "Itinerary could not be saved.");
    }
  };

  const field =
    "mt-1.5 w-full rounded-lg border border-line bg-white px-3 py-2 text-sm text-charcoal placeholder:text-charcoal-soft/60 focus:border-terracotta focus:outline-none disabled:bg-ivory";

  return (
    <div className="rounded-2xl border border-line bg-white p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
            Day-by-day itinerary
          </p>
          <p className="mt-1 text-xs text-charcoal-soft">
            {canEdit
              ? "Daily plan shown in the package detail page. Days are renumbered automatically on save."
              : "Your role can view the itinerary but only managers and admins can edit it."}
          </p>
        </div>
        {canEdit && (
          <div className="flex gap-2">
            <button
              type="button"
              onClick={renumber}
              className="rounded-full border border-line px-4 py-1.5 text-sm font-semibold text-charcoal-soft hover:text-forest"
            >
              Renumber
            </button>
            <button
              type="button"
              onClick={addRow}
              className="rounded-full border border-forest/30 px-4 py-1.5 text-sm font-semibold text-forest hover:bg-forest hover:text-ivory"
            >
              + Add day
            </button>
          </div>
        )}
      </div>

      {rows.length === 0 ? (
        <div className="mt-5 rounded-xl border border-dashed border-line py-10 text-center text-sm text-charcoal-soft">
          No itinerary days yet. {canEdit ? "Add the first day to get started." : "Check back once a manager adds the itinerary."}
        </div>
      ) : (
        <div className="mt-5 space-y-4">
          {rows.map((row, index) => (
            <div key={index} className="rounded-xl border border-line bg-ivory p-4">
              <div className="flex items-center justify-between gap-3">
                <p className="font-display text-lg text-forest">Day {row.day_number}</p>
                {canEdit && (
                  <button
                    type="button"
                    onClick={() => removeRow(index)}
                    className="rounded-full border border-terracotta/30 px-3 py-1 text-xs font-semibold text-terracotta hover:bg-terracotta hover:text-ivory"
                  >
                    Remove
                  </button>
                )}
              </div>
              <div className="mt-3 grid gap-3 sm:grid-cols-2">
                <label className="block text-xs font-semibold text-forest">
                  Title
                  <input
                    value={row.title}
                    disabled={!canEdit}
                    onChange={(e) => update(index, { title: e.target.value })}
                    placeholder="e.g. Arrival in Jaipur"
                    className={field}
                  />
                </label>
                <label className="block text-xs font-semibold text-forest">
                  Activities (comma separated)
                  <input
                    value={row.activities.join(", ")}
                    disabled={!canEdit}
                    onChange={(e) =>
                      update(index, {
                        activities: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                      })
                    }
                    placeholder="Taj Mahal, Amber Fort, bazaar walk"
                    className={field}
                  />
                </label>
                <label className="block text-xs font-semibold text-forest sm:col-span-2">
                  Description
                  <textarea
                    value={row.description}
                    disabled={!canEdit}
                    onChange={(e) => update(index, { description: e.target.value })}
                    rows={2}
                    placeholder="What happens on this day…"
                    className={field}
                  />
                </label>
                <label className="block text-xs font-semibold text-forest">
                  Meals
                  <input
                    value={row.meals}
                    disabled={!canEdit}
                    onChange={(e) => update(index, { meals: e.target.value })}
                    placeholder="Breakfast & dinner"
                    className={field}
                  />
                </label>
                <label className="block text-xs font-semibold text-forest">
                  Accommodation
                  <input
                    value={row.accommodation}
                    disabled={!canEdit}
                    onChange={(e) => update(index, { accommodation: e.target.value })}
                    placeholder="Heritage hotel, Jaipur"
                    className={field}
                  />
                </label>
                <label className="block text-xs font-semibold text-forest">
                  Transportation
                  <input
                    value={row.transportation}
                    disabled={!canEdit}
                    onChange={(e) => update(index, { transportation: e.target.value })}
                    placeholder="Private AC vehicle"
                    className={field}
                  />
                </label>
              </div>
            </div>
          ))}
        </div>
      )}

      {canEdit && (
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={save}
            disabled={saving}
            className="rounded-full bg-forest px-6 py-2 text-sm font-semibold text-ivory transition-colors hover:bg-forest-dark disabled:opacity-60"
          >
            {saving ? "Saving…" : "Save itinerary"}
          </button>
          {saved && <span className="text-sm font-semibold text-forest">Itinerary saved.</span>}
          {error && <span className="text-sm font-semibold text-terracotta">{error}</span>}
        </div>
      )}
    </div>
  );
}