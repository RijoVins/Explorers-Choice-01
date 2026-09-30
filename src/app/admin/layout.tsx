"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/components/providers";
import { isStaffRole } from "@/lib/auth";
import { Container } from "@/components/ui/Container";

const navItems = [
  { label: "Dashboard", href: "/admin" },
  { label: "Bookings", href: "/admin/bookings" },
  { label: "Enquiries", href: "/admin/enquiries" },
  { label: "Customers", href: "/admin/customers" },
  { label: "Destinations", href: "/admin/destinations" },
  { label: "Packages", href: "/admin/packages" },
  { label: "Hotels", href: "/admin/hotels" },
  { label: "Offers", href: "/admin/offers" },
  { label: "Stories", href: "/admin/stories" },
  { label: "Staff", href: "/admin/staff", adminOnly: true },
  { label: "Settings", href: "/admin/settings", adminOnly: true },
  { label: "Audit Log", href: "/admin/audit-log", managerOnly: true },
];

function isActive(pathname: string, href: string) {
  if (href === "/admin") return pathname === "/admin";
  return pathname.startsWith(href);
}

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, loading } = useAuth();
  const [navOpen, setNavOpen] = useState(false);

  useEffect(() => {
    // Access is gated by both the backend `is_staff` flag and a real staff role
    // so a mislabelled profile can never slip into the workspace. The login
    // page now honours ?redirect= only when the role may enter this area, which
    // stops the old customer → /admin → /login loop.
    if (!loading && (user === null || !user.is_staff || !isStaffRole(user.role))) {
      router.replace(`/login?redirect=${encodeURIComponent(pathname)}`);
    }
  }, [loading, user, router, pathname]);

  const isManager = user?.role === "MANAGER" || user?.role === "ADMIN";
  const visibleNav = navItems.filter((item) => {
    if (item.adminOnly && user?.role !== "ADMIN") return false;
    if (item.managerOnly && !isManager) return false;
    return true;
  });

  const activeLinkRef = (el: HTMLAnchorElement | null) => {
    if (el) {
      el.scrollIntoView({ behavior: "auto", inline: "center", block: "nearest" });
    }
  };

  if (loading || user === null || !user.is_staff || !isStaffRole(user.role)) {
    return (
      <div className="min-h-full flex items-center justify-center bg-ivory px-6">
        <p className="text-sm text-charcoal-soft">Checking workspace access…</p>
      </div>
    );
  }

  return (
    <div className="min-h-full bg-ivory text-charcoal">
      {navOpen && (
        <div
          className="fixed inset-0 z-40 bg-charcoal/40 backdrop-blur-sm"
          onClick={() => setNavOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-line bg-forest text-ivory shadow-xl transition-transform duration-200 ${
          navOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-16 items-center gap-3 border-b border-ivory/10 pl-6 pr-3">
          <div className="flex min-w-0 flex-1 flex-col">
            <Link href="/admin" className="inline-flex items-baseline gap-0.5 self-start leading-none" aria-label="Explorers Choice workspace">
              <span className="font-display text-xl tracking-tight text-ivory">Explorers</span>
              <span className="font-display text-xl text-terracotta-light">Choice</span>
            </Link>
            <span className="mt-1.5 w-fit rounded-full border border-ivory/25 px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wider text-ivory/80">
              Workspace
            </span>
          </div>
          <button
            type="button"
            onClick={() => setNavOpen(false)}
            aria-label="Close navigation"
            className="shrink-0 rounded-full p-2 text-ivory/70 transition-colors hover:bg-ivory/10 hover:text-ivory"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M18 6 6 18" />
              <path d="m6 6 12 12" />
            </svg>
          </button>
        </div>

        <nav aria-label="Workspace navigation" className="flex-1 space-y-1 overflow-y-auto px-3 py-6">
          {visibleNav.map((item) => {
            const active = isActive(pathname, item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                ref={active ? activeLinkRef : undefined}
                onClick={() => setNavOpen(false)}
                aria-current={active ? "page" : undefined}
                className={`flex items-center rounded-full px-4 py-2.5 text-sm font-semibold transition-colors ${
                  active
                    ? "bg-ivory text-forest"
                    : "text-ivory/75 hover:bg-ivory/10 hover:text-ivory"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-ivory/10 px-6 py-4">
          <Link href="/" className="block text-sm text-ivory/80 transition-colors hover:text-ivory">
            View site
          </Link>
          <div className="mt-3 flex items-center gap-3">
            <div className="flex min-w-0 flex-1 flex-col">
              <span className="truncate text-sm font-semibold text-ivory">{user.full_name || user.email}</span>
              <span className="truncate text-xs text-ivory/60">{user.email}</span>
            </div>
            <span className="rounded-full border border-terracotta-light/40 px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wider text-terracotta-light">
              {user.role}
            </span>
          </div>
        </div>
      </aside>

      <main>
        <header className="flex h-16 items-center justify-between border-b border-line bg-forest px-4 text-ivory sm:px-6">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setNavOpen(true)}
              aria-label="Open navigation"
              className="rounded-full p-2 text-ivory/80 transition-colors hover:bg-ivory/10 hover:text-ivory"
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M3 6h18" />
                <path d="M3 12h18" />
                <path d="M3 18h18" />
              </svg>
            </button>
            <Link href="/admin" className="inline-flex items-baseline gap-0.5" aria-label="Explorers Choice workspace">
              <span className="font-display text-xl tracking-tight text-ivory">Explorers</span>
              <span className="font-display text-xl text-terracotta-light">Choice</span>
            </Link>
          </div>
          <span className="truncate text-sm text-ivory/80">{user.full_name || user.email}</span>
        </header>

        <Container className="py-10 sm:py-12">{children}</Container>
      </main>
    </div>
  );
}