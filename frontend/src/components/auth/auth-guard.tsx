"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "@/context/session-context";
import { STORAGE_KEYS } from "@/lib/constants";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, token } = useSession();
  const router = useRouter();

  useEffect(() => {
    // Wait for hydration from localStorage before redirecting
    const storedToken = localStorage.getItem(STORAGE_KEYS.TOKEN);
    if (!storedToken) {
      router.replace("/login");
    }
  }, [router]);

  // Show nothing while checking auth
  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
