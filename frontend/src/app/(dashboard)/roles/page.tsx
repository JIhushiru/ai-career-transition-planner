"use client";

import { useState, useEffect, useMemo } from "react";
import { ChevronDown, ChevronRight, Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { apiGet } from "@/lib/api-client";
import type { RoleListResponse, RoleResponse } from "@/types/career";

const seniorityOptions = ["entry", "mid", "senior", "lead"];

export default function RolesPage() {
  const [roles, setRoles] = useState<RoleResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(),
  );
  const [search, setSearch] = useState("");
  const [seniorityFilter, setSeniorityFilter] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiGet<RoleListResponse>("/roles?limit=200");
        setRoles(data.roles);
      } catch {
        // silently fail
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  const hasFilters = search || seniorityFilter || remoteOnly;

  const filteredRoles = useMemo(() => {
    let result = roles;
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(
        (r) =>
          r.title.toLowerCase().includes(q) ||
          r.description?.toLowerCase().includes(q) ||
          r.category?.toLowerCase().includes(q),
      );
    }
    if (seniorityFilter) {
      result = result.filter((r) => r.seniority === seniorityFilter);
    }
    if (remoteOnly) {
      result = result.filter((r) => r.remote_friendly);
    }
    return result;
  }, [roles, search, seniorityFilter, remoteOnly]);

  const grouped = useMemo(() => {
    const groups: Record<string, RoleResponse[]> = {};
    for (const role of filteredRoles) {
      const cat = role.category || "Other";
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(role);
    }
    return Object.entries(groups).sort(([a], [b]) => a.localeCompare(b));
  }, [filteredRoles]);

  // Auto-expand all categories when searching
  useEffect(() => {
    if (hasFilters) {
      setExpandedCategories(new Set(grouped.map(([cat]) => cat)));
    }
  }, [search, seniorityFilter, remoteOnly, grouped.length]);

  const toggleCategory = (cat: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(cat)) next.delete(cat);
      else next.add(cat);
      return next;
    });
  };

  const expandAll = () => {
    setExpandedCategories(new Set(grouped.map(([cat]) => cat)));
  };

  const collapseAll = () => {
    setExpandedCategories(new Set());
  };

  const clearFilters = () => {
    setSearch("");
    setSeniorityFilter("");
    setRemoteOnly(false);
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Roles Overview</h2>
        <p className="text-muted-foreground">
          Browse all {roles.length} roles across{" "}
          {useMemo(
            () =>
              new Set(roles.map((r) => r.category || "Other")).size,
            [roles],
          )}{" "}
          categories.
        </p>
      </div>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading roles...</p>
      ) : (
        <>
          {/* Search & Filters */}
          <div className="space-y-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search roles, categories, or descriptions..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
              />
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <select
                className="rounded-md border bg-background px-3 py-1.5 text-sm"
                value={seniorityFilter}
                onChange={(e) => setSeniorityFilter(e.target.value)}
              >
                <option value="">All levels</option>
                {seniorityOptions.map((s) => (
                  <option key={s} value={s}>
                    {s.charAt(0).toUpperCase() + s.slice(1)}
                  </option>
                ))}
              </select>

              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={remoteOnly}
                  onChange={(e) => setRemoteOnly(e.target.checked)}
                  className="rounded"
                />
                Remote only
              </label>

              {hasFilters && (
                <button
                  onClick={clearFilters}
                  className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                  <X className="h-3 w-3" />
                  Clear filters
                </button>
              )}

              <span className="ml-auto text-xs text-muted-foreground">
                {filteredRoles.length} role{filteredRoles.length !== 1 ? "s" : ""}
                {hasFilters ? " found" : ""}
              </span>
            </div>
          </div>

          {/* Expand/Collapse */}
          <div className="flex gap-2">
            <button
              onClick={expandAll}
              className="text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              Expand all
            </button>
            <span className="text-xs text-muted-foreground">/</span>
            <button
              onClick={collapseAll}
              className="text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              Collapse all
            </button>
          </div>

          {/* Role List */}
          {grouped.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              No roles match your filters.
            </p>
          ) : (
            <div className="space-y-1">
              {grouped.map(([category, categoryRoles]) => {
                const isExpanded = expandedCategories.has(category);
                return (
                  <div key={category}>
                    <button
                      onClick={() => toggleCategory(category)}
                      className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-left hover:bg-muted transition-colors"
                    >
                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
                      ) : (
                        <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
                      )}
                      <span className="font-medium">{category}</span>
                      <span className="text-xs text-muted-foreground">
                        ({categoryRoles.length})
                      </span>
                    </button>
                    {isExpanded && (
                      <div className="ml-9 border-l pl-4 pb-2">
                        {categoryRoles.map((role) => (
                          <div
                            key={role.id}
                            className="py-2 border-b last:border-b-0"
                          >
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium">
                                {role.title}
                              </span>
                              {role.seniority && (
                                <Badge variant="outline" className="text-[10px]">
                                  {role.seniority}
                                </Badge>
                              )}
                              {role.remote_friendly && (
                                <Badge variant="outline" className="text-[10px]">
                                  Remote
                                </Badge>
                              )}
                            </div>
                            {role.description && (
                              <p className="mt-0.5 text-xs text-muted-foreground">
                                {role.description}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}
