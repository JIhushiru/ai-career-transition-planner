"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  FileText,
  Tags,
  Compass,
  Route,
  GraduationCap,
  LayoutDashboard,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/resume", label: "Resume", icon: FileText },
  { href: "/skills", label: "Skills", icon: Tags },
  { href: "/explore", label: "Explore Careers", icon: Compass, disabled: true },
  { href: "/transitions", label: "Career GPS", icon: Route, disabled: true },
  {
    href: "/roadmap",
    label: "Roadmap",
    icon: GraduationCap,
    disabled: true,
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-64 flex-col border-r bg-card">
      <div className="flex h-14 items-center border-b px-4">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <Compass className="h-5 w-5 text-primary" />
          <span>Career Planner</span>
        </Link>
      </div>
      <nav className="flex-1 space-y-1 p-3">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.disabled ? "#" : item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                isActive
                  ? "bg-primary/10 font-medium text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
                item.disabled && "pointer-events-none opacity-40",
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
              {item.disabled && (
                <span className="ml-auto text-[10px] uppercase tracking-wider opacity-60">
                  Soon
                </span>
              )}
            </Link>
          );
        })}
      </nav>
      <div className="border-t p-4 text-xs text-muted-foreground">
        AI Career Transition Planner v0.1
      </div>
    </aside>
  );
}
