export type UserProfile = {
  id: number;
  email: string;
  full_name: string;
  phone: string;
  country: string;
  role: string;
  auth_provider?: "EMAIL" | "GOOGLE";
  is_staff: boolean;
  created_at: string;
};

export type RegisterPayload = {
  email: string;
  password: string;
  full_name: string;
  phone: string;
  country: string;
  requested_role?: "CUSTOMER" | "TRAVEL_AGENT" | "HOTEL_OWNER";
};

export type LoginPayload = {
  email: string;
  password: string;
};

import { getApiBaseUrl, CLIENT_API_URL as API_URL } from "@/lib/api";

function apiErrorMessage(body: unknown, fallback: string): string {
  if (!body || typeof body !== "object" || !("detail" in body)) return fallback;

  const detail = body.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const messages = detail.map((item) => {
      if (typeof item === "string") return item;
      if (item && typeof item === "object" && "msg" in item && typeof item.msg === "string") {
        return item.msg;
      }
      return null;
    }).filter((message): message is string => Boolean(message));
    if (messages.length > 0) return messages.join(" ");
  }

  return fallback;
}

export async function registerUser(payload: RegisterPayload): Promise<UserProfile> {
  const apiBase = getApiBaseUrl();
  const response = await fetch(`${apiBase}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload),
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) throw new Error(apiErrorMessage(body, "We could not create your account. Please try again."));
  return body as UserProfile;
}

export async function loginUser(payload: LoginPayload): Promise<UserProfile> {
  const apiBase = getApiBaseUrl();
  const response = await fetch(`${apiBase}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload),
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) throw new Error(apiErrorMessage(body, "Incorrect email or password."));
  return body as UserProfile;
}

export async function logoutUser(): Promise<void> {
  const apiBase = getApiBaseUrl();
  await fetch(`${apiBase}/api/auth/logout`, { method: "POST", credentials: "include" });
}

export async function fetchCurrentUser(): Promise<UserProfile | null> {
  try {
    const apiBase = getApiBaseUrl();
    const response = await fetch(`${apiBase}/api/auth/me`, {
      credentials: "include",
    });
    if (!response.ok) return null;
    return (await response.json()) as UserProfile;
  } catch {
    return null;
  }
}

export async function updateProfile(updates: Partial<Pick<UserProfile, "full_name" | "phone" | "country">>): Promise<UserProfile> {
  const apiBase = getApiBaseUrl();
  const response = await fetch(`${apiBase}/api/auth/me`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(updates),
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) throw new Error(apiErrorMessage(body, "Your profile could not be updated."));
  return body as UserProfile;
}

export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
  const apiBase = getApiBaseUrl();
  const response = await fetch(`${apiBase}/api/auth/change-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) throw new Error(apiErrorMessage(body, "Your password could not be changed."));
}

export async function requestPasswordReset(email: string): Promise<void> {
  const apiBase = getApiBaseUrl();
  const response = await fetch(`${apiBase}/api/auth/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email }),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(apiErrorMessage(body, "We could not send a reset link."));
  }
}

export async function resetPassword(token: string, password: string): Promise<void> {
  const apiBase = getApiBaseUrl();
  const response = await fetch(`${apiBase}/api/auth/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ token, password }),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(apiErrorMessage(body, "This reset link is invalid or has expired."));
  }
}

/**
 * Build a URL that sends the browser through the backend-driven Google OAuth
 * flow. The `next` path is where the user lands after a successful sign-in
 * (validated server-side to a local path).
 */
export function googleLoginUrl(next?: string): string {
  const path = next && next.startsWith("/") && !next.startsWith("//") ? next : "/account";
  return `${API_URL}/auth/google?next=${encodeURIComponent(path)}`;
}

const STAFF_ROLES = new Set(["TRAVEL_AGENT", "MANAGER", "ACCOUNTANT", "ADMIN"]);

/** A user is staff only when their role is in STAFF_ROLES — never is_staff alone. */
export function isStaffRole(role?: string | null): boolean {
  return Boolean(role && STAFF_ROLES.has(role));
}

const STAFF_PREFIXES = ["/admin"];
const OWNER_PREFIXES = ["/hotel-owner"];

/**
 * Decide where a just-signed-in user may go. `requested` (the ?redirect= value)
 * is honoured only when it belongs to an area their role can actually enter —
 * otherwise they get their role's default landing page. This prevents the
 * login?redirect=/admin loop that hit customers who were redirected from /admin
 * and then bounced straight back.
 */
export function postLoginPath(user: UserProfile, requested?: string | null): string {
  const path = requested && requested.startsWith("/") && !requested.startsWith("//")
    ? requested
    : "/account";
  if (isStaffRole(user.role)) {
    return STAFF_PREFIXES.some((p) => path === p || path.startsWith(`${p}/`))
      ? path
      : "/admin";
  }
  if (user.role === "HOTEL_OWNER") {
    return OWNER_PREFIXES.some((p) => path === p || path.startsWith(`${p}/`))
      ? path
      : "/hotel-owner";
  }
  const restricted = [...STAFF_PREFIXES, ...OWNER_PREFIXES];
  if (restricted.some((p) => path === p || path.startsWith(`${p}/`))) {
    return "/account";
  }
  return path;
}

/** Default landing page for a signed-in user's role. */
export function roleHomePath(user: UserProfile): string {
  if (isStaffRole(user.role)) return "/admin";
  if (user.role === "HOTEL_OWNER") return "/hotel-owner";
  return "/account";
}