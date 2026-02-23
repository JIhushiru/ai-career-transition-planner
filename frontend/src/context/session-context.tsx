"use client";

import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { STORAGE_KEYS, clearSessionStorage } from "@/lib/constants";

interface SessionState {
  userId: number | null;
  resumeId: number | null;
  token: string | null;
  email: string | null;
  name: string | null;
  currentSalary: number | null;
}

interface SessionContextValue extends SessionState {
  isAuthenticated: boolean;
  setSession: (userId: number, resumeId: number) => void;
  login: (token: string, userId: number, email: string, name?: string | null) => void;
  logout: () => void;
  setCurrentSalary: (salary: number | null) => void;
}

const SessionContext = createContext<SessionContextValue | null>(null);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [session, _setSession] = useState<SessionState>({
    userId: null,
    resumeId: null,
    token: null,
    email: null,
    name: null,
    currentSalary: null,
  });

  useEffect(() => {
    const storedToken = localStorage.getItem(STORAGE_KEYS.TOKEN);
    const storedUser = localStorage.getItem(STORAGE_KEYS.USER_ID);
    const storedResume = localStorage.getItem(STORAGE_KEYS.RESUME_ID);
    const storedEmail = localStorage.getItem(STORAGE_KEYS.EMAIL);
    const storedName = localStorage.getItem(STORAGE_KEYS.NAME);
    const storedSalary = localStorage.getItem(STORAGE_KEYS.SALARY);
    if (storedToken && storedUser) {
      _setSession({
        token: storedToken,
        userId: parseInt(storedUser, 10),
        resumeId: storedResume ? parseInt(storedResume, 10) : null,
        email: storedEmail,
        name: storedName,
        currentSalary: storedSalary ? parseInt(storedSalary, 10) : null,
      });
    }
  }, []);

  const login = useCallback(
    (token: string, userId: number, email: string, name?: string | null) => {
      _setSession((prev) => ({ ...prev, token, userId, email, name: name ?? null }));
      localStorage.setItem(STORAGE_KEYS.TOKEN, token);
      localStorage.setItem(STORAGE_KEYS.USER_ID, String(userId));
      localStorage.setItem(STORAGE_KEYS.EMAIL, email);
      if (name) localStorage.setItem(STORAGE_KEYS.NAME, name);
    },
    [],
  );

  const logout = useCallback(() => {
    _setSession({ userId: null, resumeId: null, token: null, email: null, name: null, currentSalary: null });
    clearSessionStorage();
  }, []);

  const setSession = useCallback((userId: number, resumeId: number) => {
    _setSession((prev) => ({ ...prev, userId, resumeId }));
    localStorage.setItem(STORAGE_KEYS.USER_ID, String(userId));
    localStorage.setItem(STORAGE_KEYS.RESUME_ID, String(resumeId));
  }, []);

  const setCurrentSalary = useCallback((salary: number | null) => {
    _setSession((prev) => ({ ...prev, currentSalary: salary }));
    if (salary != null) {
      localStorage.setItem(STORAGE_KEYS.SALARY, String(salary));
    } else {
      localStorage.removeItem(STORAGE_KEYS.SALARY);
    }
  }, []);

  return (
    <SessionContext.Provider
      value={{
        ...session,
        isAuthenticated: !!session.token,
        setSession,
        login,
        logout,
        setCurrentSalary,
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
