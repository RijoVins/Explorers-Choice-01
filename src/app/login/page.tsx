"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Container } from "@/components/ui/Container";
import { Button } from "@/components/ui/Button";
import { GoogleSignInButton } from "@/components/ui/GoogleSignInButton";
import { useAuth } from "@/components/providers";
import { postLoginPath, roleHomePath } from "@/lib/auth";

const fieldClasses =
  "w-full rounded-xl border border-line bg-white px-4 py-3 text-sm text-charcoal placeholder:text-charcoal-soft/60 focus:border-terracotta focus:outline-none";

function googleAuthErrorMessage(code: string): string {
  if (code === "email_unverified") return "Google could not verify this email address. Please use a different account.";
  if (code === "state_error") return "Your Google sign-in session expired. Please try again.";
  if (code === "account_exists_with_password") {
    return "An account with this email already exists with a password. Please sign in with your email and password instead.";
  }
  return "Google sign-in could not be completed. Please try again or sign in with your email.";
}

function LoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const rawRedirect = searchParams.get("redirect") ?? "/account";
  const redirect = rawRedirect.startsWith("/") && !rawRedirect.startsWith("//") ? rawRedirect : "/account";
  const googleAuthError = searchParams.get("google_auth");
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(
    googleAuthError ? googleAuthErrorMessage(googleAuthError) : ""
  );
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      const loggedInUser = await login(email, password);

      // Only honour an explicit ?redirect= when the user's role may enter that
      // area. Otherwise fall back to their role's home page. This stops a
      // customer bounced from /admin from looping between /admin and /login.
      const target = searchParams.has("redirect")
        ? postLoginPath(loggedInUser, rawRedirect)
        : roleHomePath(loggedInUser);
      router.push(target);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign in failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Container className="flex flex-1 flex-col items-center justify-center py-20">
      <div className="w-full max-w-sm">
        <p className="mb-4 text-center text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
          Welcome back
        </p>
        <h1 className="text-center font-display text-4xl text-forest">Login</h1>
        <p className="mt-4 text-center text-sm text-charcoal-soft">
          Sign in to view your bookings, manage payments and access your travel documents.
        </p>
        <form onSubmit={handleSubmit} className="mt-8 space-y-5">
          {error && <p className="rounded-xl border border-terracotta/30 bg-terracotta/10 p-4 text-sm text-charcoal">{error}</p>}
          <div>
            <label htmlFor="email" className="mb-2 block text-sm font-semibold text-forest">Email</label>
            <input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@email.com" className={fieldClasses} />
          </div>
          <div>
            <label htmlFor="password" className="mb-2 block text-sm font-semibold text-forest">Password</label>
            <input id="password" type="password" required autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" className={fieldClasses} />
          </div>
          <Button type="submit" variant="primary" size="lg" className="w-full" ariaLabel="Sign in" disabled={loading}>
            {loading ? "Signing in…" : "Sign in"}
          </Button>
        </form>
        <div className="my-6 flex items-center gap-3">
          <span className="h-px flex-1 bg-line" />
          <span className="text-xs uppercase tracking-[0.2em] text-charcoal-soft">or</span>
          <span className="h-px flex-1 bg-line" />
        </div>
        <GoogleSignInButton next={redirect} />

        <p className="mt-6 text-center text-sm text-charcoal-soft">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="font-semibold text-terracotta hover:underline">Create one</Link>
        </p>
        <p className="mt-4 text-center text-sm text-charcoal-soft">
          <Link href="/forgot-password" className="font-semibold text-terracotta hover:underline">Forgot your password?</Link>
        </p>
      </div>
    </Container>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<Container className="py-20 text-center text-charcoal-soft">Loading…</Container>}>
      <LoginContent />
    </Suspense>
  );
}
