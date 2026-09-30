import Link from "next/link";
import { Container } from "@/components/ui/Container";
import { Logo } from "@/components/layout/Header";

const exploreLinks = [
  { label: "Destinations", href: "/destinations" },
  { label: "Packages", href: "/packages" },
  { label: "Hotels", href: "/hotels" },
  { label: "Train Booking", href: "/trains" },
  { label: "Cab Booking", href: "/cabs" },
];

const companyLinks = [
  { label: "About", href: "/about" },
  { label: "Customer Stories", href: "/stories" },
  { label: "FAQ", href: "/faq" },
  { label: "Contact", href: "/contact" },
  { label: "Login", href: "/login" },
];

function InstagramIcon({ className = "h-5 w-5" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect width="20" height="20" x="2" y="2" rx="5" ry="5" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="17.5" cy="6.5" r="1.2" fill="currentColor" stroke="none" />
    </svg>
  );
}

function GmailIcon({ className = "h-5 w-5" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden="true"
    >
      <path d="M24 5.457v13.909c0 .904-.732 1.636-1.636 1.636h-3.819V11.73L12 16.64l-6.545-4.91v9.272H1.636A1.636 1.636 0 0 1 0 19.366V5.457c0-2.023 2.309-3.178 3.927-1.964L5.455 4.64 12 9.548l6.545-4.91 1.528-1.145C21.69 2.28 24 3.434 24 5.457z" />
    </svg>
  );
}

export function Footer() {
  return (
    <footer className="mt-24 border-t border-line bg-ivory-warm">
      <Container className="py-16">
        <div className="grid gap-12 md:grid-cols-2 lg:grid-cols-4">
          <div className="lg:col-span-1">
            <Logo />
            <p className="mt-5 max-w-xs text-sm leading-relaxed text-charcoal-soft">
              Carefully chosen journeys, memorable places, and a travel team that
              handles the details.
            </p>
            <div className="mt-6 flex items-center gap-3">
              <a
                href="https://www.instagram.com/explorerschoice_tours?stkn=NHRqYmdxdDNqajNp"
                target="_blank"
                rel="noopener noreferrer"
                className="flex h-10 w-10 items-center justify-center rounded-full border border-forest/20 text-forest transition-colors hover:bg-forest hover:text-ivory"
                aria-label="Instagram"
                title="Instagram"
              >
                <InstagramIcon className="h-5 w-5" />
              </a>
              <a
                href="https://mail.google.com/mail/?view=cm&fs=1&to=infoexplorerschoice@gmail.com"
                target="_blank"
                rel="noopener noreferrer"
                className="flex h-10 w-10 items-center justify-center rounded-full border border-forest/20 text-forest transition-colors hover:bg-forest hover:text-ivory"
                aria-label="Gmail"
                title="Gmail"
              >
                <GmailIcon className="h-5 w-5" />
              </a>
            </div>
          </div>

          <div>
            <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
              Explore
            </h3>
            <ul className="mt-5 space-y-3">
              {exploreLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-charcoal-soft transition-colors hover:text-forest"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
              Company
            </h3>
            <ul className="mt-5 space-y-3">
              {companyLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-charcoal-soft transition-colors hover:text-forest"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
              Ready to travel?
            </h3>
            <p className="mt-5 text-sm text-charcoal-soft">
              Talk to a real travel planner about your next journey.
            </p>
            <Link
              href="/book#trip"
              className="mt-5 inline-flex items-center justify-center rounded-full bg-terracotta px-6 py-3 text-sm font-semibold text-ivory transition-colors hover:bg-terracotta-dark"
            >
              Book Now
            </Link>
          </div>
        </div>

        <div className="mt-16 flex flex-col items-center justify-between gap-4 border-t border-line pt-8 sm:flex-row">
          <p className="text-xs text-charcoal-soft">
            © {new Date().getFullYear()} Explorers Choice. All rights reserved.
          </p>
          <div className="flex gap-6">
            <a href="#" className="text-xs text-charcoal-soft hover:text-forest">
              Privacy
            </a>
            <a href="#" className="text-xs text-charcoal-soft hover:text-forest">
              Terms
            </a>
            <a href="#" className="text-xs text-charcoal-soft hover:text-forest">
              Booking conditions
            </a>
          </div>
        </div>
      </Container>
    </footer>
  );
}
