"use client";

import { useState, useEffect, useMemo } from "react";
import { FolderOpen, Briefcase, ChevronDown } from "lucide-react";
import { apiGet } from "@/lib/api-client";
import type { RoleListResponse, RoleResponse } from "@/types/career";

interface RolePickerProps {
  selectedRoleId: number | null;
  onSelect: (roleId: number) => void;
  label?: string;
}

export function RolePicker({
  selectedRoleId,
  onSelect,
  label = "Target Role",
}: RolePickerProps) {
  const [roles, setRoles] = useState<RoleResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState("");

  useEffect(() => {
    async function loadRoles() {
      try {
        const data = await apiGet<RoleListResponse>("/roles?limit=300");
        setRoles(data.roles);
      } catch {
        // Roles list is non-critical — page still renders without it
      } finally {
        setIsLoading(false);
      }
    }
    loadRoles();
  }, []);

  const grouped = useMemo(() => {
    const groups: Record<string, RoleResponse[]> = {};
    for (const role of roles) {
      const cat = role.category || "Other";
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(role);
    }
    return groups;
  }, [roles]);

  const categories = useMemo(
    () => Object.keys(grouped).sort(),
    [grouped],
  );

  const filteredRoles = selectedCategory ? grouped[selectedCategory] || [] : [];

  if (isLoading) {
    return (
      <div className="space-y-2">
        <label className="block text-xs font-medium text-muted-foreground uppercase tracking-wide">
          {label}
        </label>
        <div className="h-10 animate-pulse rounded-lg bg-muted" />
        <div className="h-10 animate-pulse rounded-lg bg-muted" />
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <label className="block text-xs font-medium text-muted-foreground uppercase tracking-wide">
        {label}
      </label>
      <div className="relative">
        <FolderOpen className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <select
          className="h-10 w-full appearance-none rounded-lg border bg-background pl-9 pr-9 text-sm font-medium transition-colors hover:border-foreground/25 focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/20"
          value={selectedCategory}
          onChange={(e) => {
            setSelectedCategory(e.target.value);
          }}
        >
          <option value="" disabled>
            Select a category...
          </option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat} ({grouped[cat].length})
            </option>
          ))}
        </select>
        <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      </div>

      <div className="relative">
        <Briefcase className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <select
          className={`h-10 w-full appearance-none rounded-lg border bg-background pl-9 pr-9 text-sm font-medium transition-colors focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/20 ${
            !selectedCategory
              ? "cursor-not-allowed opacity-50"
              : "hover:border-foreground/25"
          }`}
          value={selectedRoleId ?? ""}
          onChange={(e) => onSelect(parseInt(e.target.value))}
          disabled={!selectedCategory}
        >
          <option value="" disabled>
            Select a role...
          </option>
          {filteredRoles.map((role) => (
            <option key={role.id} value={role.id}>
              {role.title}
              {role.seniority ? ` (${role.seniority})` : ""}
            </option>
          ))}
        </select>
        <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      </div>
    </div>
  );
}
