"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import {
  fetchCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
  type RegisterPayload,
  type UserProfile,
} from "@/lib/auth";

type AuthContextType = {
  user: UserProfile | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<UserProfile>;
  register: (data: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const current = await fetchCurrentUser();
    setUser(current);
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    refresh().finally(() => setLoading(false));
  }, [refresh]);

  const login = useCallback(async (email: string, password: string) => {
    const current = await loginUser({ email, password });
    setUser(current);
    return current;
  }, []);

  const register = useCallback(async (data: RegisterPayload) => {
    const current = await registerUser(data);
    setUser(current);
  }, []);

  const logout = useCallback(async () => {
    // Sign the user out locally even if the backend call fails — an error on
    // logout must never leave someone thinking they are still signed in, and a
    // stale server session will simply be cleared on their next request.
    try {
      await logoutUser();
    } finally {
      setUser(null);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, loading, login, register, logout, refresh }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
}
