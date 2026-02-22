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
  const [isLoading, setIsLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState("");

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
    return <p className="text-sm text-muted-foreground">Loading roles...</p>;
  }

  return (
    <div className="space-y-2">
      <label className="mb-1 block text-xs font-medium">{label}</label>
      <select
        className="w-full rounded-md border bg-background px-3 py-2 text-sm"
        value={selectedCategory}
        onChange={(e) => {
          setSelectedCategory(e.target.value);
          // Reset role selection when category changes
        }}
      >
        <option value="">Select a category...</option>
        {categories.map((cat) => (
          <option key={cat} value={cat}>
            {cat} ({grouped[cat].length})
          </option>
        ))}
      </select>

      <select
        className="w-full rounded-md border bg-background px-3 py-2 text-sm"
        value={selectedRoleId ?? ""}
        onChange={(e) => onSelect(parseInt(e.target.value))}
        disabled={!selectedCategory}
      >
        <option value="">Select a role...</option>
        {filteredRoles.map((role) => (
          <option key={role.id} value={role.id}>
            {role.title}{role.seniority ? ` (${role.seniority})` : ""}
          </option>
        ))}
      </select>
    </div>
  );
}
