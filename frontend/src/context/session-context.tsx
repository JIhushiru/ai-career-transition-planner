"use client";

import { createContext, useContext, useState, useEffect, useCallback } from "react";

interface SessionState {
  userId: number | null;
  resumeId: number | null;
  token: string | null;
  email: string | null;
  name: string | null;
}

interface SessionContextValue extends SessionState {
  isAuthenticated: boolean;
  setSession: (userId: number, resumeId: number) => void;
  login: (token: string, userId: number, email: string, name?: string | null) => void;
  logout: () => void;
  clearSession: () => void;
}

const SessionContext = createContext<SessionContextValue | null>(null);

const STORAGE_KEY_USER = "ct_user_id";
const STORAGE_KEY_RESUME = "ct_resume_id";
const STORAGE_KEY_TOKEN = "ct_token";
const STORAGE_KEY_EMAIL = "ct_email";
const STORAGE_KEY_NAME = "ct_name";

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [session, _setSession] = useState<SessionState>({
    userId: null,
    resumeId: null,
    token: null,
    email: null,
    name: null,
  });

  useEffect(() => {
    const storedToken = localStorage.getItem(STORAGE_KEY_TOKEN);
    const storedUser = localStorage.getItem(STORAGE_KEY_USER);
    const storedResume = localStorage.getItem(STORAGE_KEY_RESUME);
    const storedEmail = localStorage.getItem(STORAGE_KEY_EMAIL);
    const storedName = localStorage.getItem(STORAGE_KEY_NAME);
    if (storedToken && storedUser) {
      _setSession({
        token: storedToken,
        userId: parseInt(storedUser, 10),
        resumeId: storedResume ? parseInt(storedResume, 10) : null,
        email: storedEmail,
        name: storedName,
      });
    }
  }, []);

  const login = useCallback(
    (token: string, userId: number, email: string, name?: string | null) => {
      _setSession((prev) => ({ ...prev, token, userId, email, name: name ?? null }));
      localStorage.setItem(STORAGE_KEY_TOKEN, token);
      localStorage.setItem(STORAGE_KEY_USER, String(userId));
      localStorage.setItem(STORAGE_KEY_EMAIL, email);
      if (name) localStorage.setItem(STORAGE_KEY_NAME, name);
    },
    [],
  );

  const logout = useCallback(() => {
    _setSession({ userId: null, resumeId: null, token: null, email: null, name: null });
    localStorage.removeItem(STORAGE_KEY_TOKEN);
    localStorage.removeItem(STORAGE_KEY_USER);
    localStorage.removeItem(STORAGE_KEY_RESUME);
    localStorage.removeItem(STORAGE_KEY_EMAIL);
    localStorage.removeItem(STORAGE_KEY_NAME);
  }, []);

  const setSession = useCallback((userId: number, resumeId: number) => {
    _setSession((prev) => ({ ...prev, userId, resumeId }));
    localStorage.setItem(STORAGE_KEY_USER, String(userId));
    localStorage.setItem(STORAGE_KEY_RESUME, String(resumeId));
  }, []);

  const clearSession = logout;

  return (
    <SessionContext.Provider
      value={{
        ...session,
        isAuthenticated: !!session.token,
        setSession,
        login,
        logout,
        clearSession,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error("useSession must be used within SessionProvider");
  return ctx;
}
