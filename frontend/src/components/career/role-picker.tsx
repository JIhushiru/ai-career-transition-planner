"use client";

import { useState, useEffect, useMemo } from "react";
import { ChevronLeft } from "lucide-react";
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
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

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

  const selectedRole = useMemo(
    () => roles.find((r) => r.id === selectedRoleId),
    [roles, selectedRoleId],
  );

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading roles...</p>;
  }

  return (
    <div>
      <label className="mb-1 block text-xs font-medium">{label}</label>

      {selectedRole && (
        <p className="mb-2 rounded-md border border-primary/30 bg-primary/5 px-3 py-1.5 text-sm font-medium">
          {selectedRole.title}
          {selectedRole.seniority ? ` (${selectedRole.seniority})` : ""}
          <span className="ml-1 text-xs text-muted-foreground">
            — {selectedRole.category}
          </span>
        </p>
      )}

      {!selectedCategory ? (
        <div className="grid grid-cols-2 gap-2">
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setSelectedCategory(cat)}
              className="rounded-md border bg-background px-3 py-2 text-left text-sm hover:bg-accent hover:text-accent-foreground transition-colors"
            >
              <span className="font-medium">{cat}</span>
              <span className="ml-1 text-xs text-muted-foreground">
                ({grouped[cat].length})
              </span>
            </button>
          ))}
        </div>
      ) : (
        <div>
          <button
            type="button"
            onClick={() => setSelectedCategory(null)}
            className="mb-2 flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            <ChevronLeft className="h-3 w-3" />
            Back to categories
          </button>
          <div className="max-h-48 space-y-1 overflow-y-auto rounded-md border p-1">
            {grouped[selectedCategory].map((role) => (
              <button
                key={role.id}
                type="button"
                onClick={() => onSelect(role.id)}
                className={`w-full rounded px-3 py-1.5 text-left text-sm transition-colors ${
                  selectedRoleId === role.id
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-accent hover:text-accent-foreground"
                }`}
              >
                {role.title}
                {role.seniority ? (
                  <span className="ml-1 text-xs opacity-70">
                    ({role.seniority})
                  </span>
                ) : null}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
