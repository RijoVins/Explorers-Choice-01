import type React from "react";

export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return (
    <div
      className="flex flex-col items-center justify-center gap-4 py-24 text-center"
      role="status"
      aria-live="polite"
    >
      <span className="h-10 w-10 animate-spin rounded-full border-2 border-forest/20 border-t-forest" />
      <p className="text-sm font-semibold text-charcoal-soft">{label}</p>
      <span className="sr-only">Loading</span>
    </div>
  );
}

export function ErrorState({
  title = "We could not load this right now",
  message = "Please try again in a moment.",
  action,
}: {
  title?: string;
  message?: string;
  action?: React.ReactNode;
}) {
  return (
    <div
      className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-line bg-sand/40 py-20 text-center"
      role="alert"
    >
      <svg
        className="h-12 w-12 text-terracotta"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M12 8v5" />
        <path d="M12 16.5h.01" />
        <circle cx="12" cy="12" r="9" />
      </svg>
      <h3 className="font-display text-2xl text-forest">{title}</h3>
      <p className="max-w-sm text-sm text-charcoal-soft">{message}</p>
      {action}
    </div>
  );
}

export function EmptyState({
  title = "Nothing here yet",
  message = "Please check back soon.",
}: {
  title?: string;
  message?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-line py-24 text-center">
      <svg
        className="h-12 w-12 text-sand"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <circle cx="12" cy="12" r="9" />
        <path d="M12 8h.01M12 12v4" />
      </svg>
      <h3 className="font-display text-2xl text-forest">{title}</h3>
      <p className="max-w-sm text-sm text-charcoal-soft">{message}</p>
    </div>
  );
}
