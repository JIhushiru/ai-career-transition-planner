"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  FileText,
  Tags,
  Compass,
  Route,
  GraduationCap,
  LayoutDashboard,
  LogOut,
  Briefcase,
  Star,
  ClipboardCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useSession } from "@/context/session-context";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/resume", label: "Resume", icon: FileText },
  { href: "/skills", label: "Skills", icon: Tags },
  { href: "/roles", label: "Roles", icon: Briefcase },
  { href: "/explore", label: "Explore Careers", icon: Compass },
  { href: "/transitions", label: "Career GPS", icon: Route },
  { href: "/roadmap", label: "Roadmap", icon: GraduationCap },
  { href: "/dream-job", label: "Dream Job", icon: Star },
  { href: "/assessment", label: "Self-Assessment", icon: ClipboardCheck },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { email, name, logout } = useSession();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

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
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                isActive
                  ? "bg-primary/10 font-medium text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t p-3">
        {email && (
          <div className="mb-2 truncate px-3 text-xs text-muted-foreground">
            {name || email}
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
