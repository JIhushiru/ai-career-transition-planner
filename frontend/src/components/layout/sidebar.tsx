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
  BookOpen,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useSession } from "@/context/session-context";

const navGroups = [
  {
    label: "Overview",
    items: [
      { href: "/", label: "Dashboard", icon: LayoutDashboard },
    ],
  },
  {
    label: "Resume & Skills",
    items: [
      { href: "/resume", label: "Resume", icon: FileText },
      { href: "/skills", label: "Skills", icon: Tags },
      { href: "/assessment", label: "Self-Assessment", icon: ClipboardCheck },
    ],
  },
  {
    label: "Career Matching",
    items: [
      { href: "/roles", label: "Roles", icon: Briefcase },
      { href: "/explore", label: "Explore Careers", icon: Compass },
    ],
  },
  {
    label: "Learning",
    items: [
      { href: "/datacamp", label: "DataCamp Tracks", icon: BookOpen },
    ],
  },
  {
    label: "Planning",
    items: [
      { href: "/transitions", label: "Career GPS", icon: Route },
      { href: "/roadmap", label: "Roadmap", icon: GraduationCap },
      { href: "/dream-job", label: "Dream Job", icon: Star },
    ],
  },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { email, name, logout } = useSession();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const handleNavClick = () => {
    onClose?.();
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r bg-sidebar transition-transform duration-200 md:static md:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex h-14 items-center justify-between border-b px-4">
          <Link
            href="/"
            className="flex items-center gap-2 font-semibold text-primary"
            onClick={handleNavClick}
          >
            <Compass className="h-5 w-5" />
            <span>Career Planner</span>
          </Link>
          <button
            className="rounded-md p-1.5 text-muted-foreground hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring md:hidden"
            onClick={onClose}
            aria-label="Close menu"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 py-4">
          {navGroups.map((group) => (
            <div key={group.label} className="mb-4">
              <p className="mb-1.5 px-3 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/70">
                {group.label}
              </p>
              <div className="space-y-0.5">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = pathname === item.href;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={handleNavClick}
                      className={cn(
                        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                        isActive
                          ? "bg-primary/10 font-medium text-primary"
                          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                      )}
                    >
                      <Icon className="h-4 w-4 shrink-0" />
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="border-t p-3">
          {email && (
            <div className="mb-2 truncate px-3 text-xs text-muted-foreground">
              {name || email}
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </aside>
    </>
  );
}
