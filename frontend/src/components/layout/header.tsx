"use client";

import { usePathname } from "next/navigation";
import { useTheme } from "next-themes";
import { Sun, Moon } from "lucide-react";

const pageTitles: Record<string, string> = {
  "/": "Dashboard",
  "/resume": "Resume Parser",
  "/skills": "Extracted Skills",
  "/explore": "Explore Careers",
  "/transitions": "Career GPS",
  "/roadmap": "Learning Roadmap",
  "/roles": "Roles Overview",
  "/dream-job": "Dream Job Planner",
  "/assessment": "Skills Assessment",
};

export function Header() {
  const pathname = usePathname();
  const title = pageTitles[pathname] || "Career Planner";
  const { theme, setTheme } = useTheme();

  return (
    <header className="flex h-14 items-center justify-between border-b bg-card px-6">
      <h1 className="text-lg font-semibold">{title}</h1>
      <button
        aria-label="Toggle theme"
        onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        className="rounded-md p-2 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
      >
        <Sun className="h-4 w-4 dark:hidden" />
        <Moon className="hidden h-4 w-4 dark:block" />
      </button>
    </header>
  );
}
