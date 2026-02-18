"use client";

import { usePathname } from "next/navigation";

const pageTitles: Record<string, string> = {
  "/": "Dashboard",
  "/resume": "Resume Parser",
  "/skills": "Extracted Skills",
  "/explore": "Explore Careers",
  "/transitions": "Career GPS",
  "/roadmap": "Learning Roadmap",
};

export function Header() {
  const pathname = usePathname();
  const title = pageTitles[pathname] || "Career Planner";

  return (
    <header className="flex h-14 items-center border-b bg-card px-6">
      <h1 className="text-lg font-semibold">{title}</h1>
    </header>
  );
}
