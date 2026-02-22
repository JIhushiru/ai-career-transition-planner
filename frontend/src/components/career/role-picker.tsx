"use client";

import { useState, useEffect, useMemo } from "react";
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
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadRoles() {
      try {
        const data = await apiGet<RoleListResponse>("/roles?limit=200");
        setRoles(data.roles);
      } catch {
        // silently fail
      } finally {
        setIsLoading(false);
      }
    }
    loadRoles();
  }, []);

  const grouped = useMemo(() => {
    const filtered = search
      ? roles.filter((r) =>
          r.title.toLowerCase().includes(search.toLowerCase()),
        )
      : roles;

    const groups: Record<string, RoleResponse[]> = {};
    for (const role of filtered) {
      const cat = role.category || "Other";
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(role);
    }
    return groups;
  }, [roles, search]);

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading roles...</p>;
  }

  return (
    <div>
      <label className="mb-1 block text-xs font-medium">{label}</label>
      <input
        type="text"
        placeholder="Search roles..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="mb-2 w-full rounded-md border bg-background px-3 py-2 text-sm"
      />
      <select
        className="w-full rounded-md border bg-background px-3 py-2 text-sm"
        value={selectedRoleId ?? ""}
        onChange={(e) => onSelect(parseInt(e.target.value))}
        size={6}
      >
        {Object.entries(grouped).map(([category, categoryRoles]) => (
          <optgroup key={category} label={category}>
            {categoryRoles.map((role) => (
              <option key={role.id} value={role.id}>
                {role.title}
                {role.seniority ? ` (${role.seniority})` : ""}
              </option>
            ))}
          </optgroup>
        ))}
      </select>
    </div>
  );
}
