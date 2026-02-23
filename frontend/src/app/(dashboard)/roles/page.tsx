"use client";

import { useState, useEffect, useMemo } from "react";
import {
  ChevronDown,
  ChevronRight,
  Search,
  X,
  Wifi,
  Briefcase,
  DollarSign,
  FolderOpen,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiGet } from "@/lib/api-client";
import { formatSalaryRange } from "@/lib/salary";
import { SENIORITY_COLORS } from "@/lib/constants";
import type { RoleListResponse, RoleResponse } from "@/types/career";

const seniorityOptions = ["entry", "mid", "senior", "lead"];

const SALARY_PRESETS = [
  { label: "Any salary", min: 0, max: 0 },
  { label: "Below 30K", min: 0, max: 30000 },
  { label: "30K - 60K", min: 30000, max: 60000 },
  { label: "60K - 100K", min: 60000, max: 100000 },
  { label: "100K - 150K", min: 100000, max: 150000 },
  { label: "150K+", min: 150000, max: 0 },
];

export default function RolesPage() {
  const [roles, setRoles] = useState<RoleResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(),
  );
  const [search, setSearch] = useState("");
  const [seniorityFilter, setSeniorityFilter] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [salaryPreset, setSalaryPreset] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiGet<RoleListResponse>("/roles?limit=300");
        setRoles(data.roles);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load roles");
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  const hasFilters = search || seniorityFilter || remoteOnly || salaryPreset > 0;

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
    if (salaryPreset > 0) {
      const preset = SALARY_PRESETS[salaryPreset];
      result = result.filter((r) => {
        if (!r.salary_min_ph && !r.salary_max_ph) return false;
        const rMin = r.salary_min_ph ?? 0;
        const rMax = r.salary_max_ph ?? rMin;
        if (preset.min > 0 && rMax < preset.min) return false;
        if (preset.max > 0 && rMin > preset.max) return false;
        return true;
      });
    }
    return result;
  }, [roles, search, seniorityFilter, remoteOnly, salaryPreset]);

  const grouped = useMemo(() => {
    const groups: Record<string, RoleResponse[]> = {};
    for (const role of filteredRoles) {
      const cat = role.category || "Other";
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(role);
    }
    return Object.entries(groups).sort(([a], [b]) => a.localeCompare(b));
  }, [filteredRoles]);

  // Only auto-expand when searching by text
  useEffect(() => {
    if (search) {
      setExpandedCategories(new Set(grouped.map(([cat]) => cat)));
    }
  }, [search, grouped.length]);

  const totalCategories = useMemo(
    () => new Set(roles.map((r) => r.category || "Other")).size,
    [roles],
  );

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
    setSalaryPreset(0);
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Roles Overview</h2>
        <p className="text-sm text-muted-foreground">
          Browse {roles.length} roles across {totalCategories} categories
        </p>
      </div>

      {error && (
        <Card className="border-destructive">
          <div role="alert" className="px-4 py-3 text-sm text-destructive">{error}</div>
        </Card>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-center space-y-2">
            <div className="mx-auto h-6 w-6 animate-spin rounded-full border-2 border-muted-foreground border-t-transparent" />
            <p className="text-sm text-muted-foreground">Loading roles...</p>
          </div>
        </div>
      ) : (
        <>
          {/* Search & Filters */}
          <Card className="gap-0 p-4 space-y-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search roles, categories, or descriptions..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
              />
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <div className="relative">
                <Briefcase className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
                <select
                  aria-label="Filter by seniority level"
                  className="h-8 appearance-none rounded-lg border bg-background pl-8 pr-8 text-sm transition-colors hover:border-foreground/25 focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/20"
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
                <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
              </div>

              <div className="relative">
                <DollarSign className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
                <select
                  aria-label="Filter by salary range"
                  className="h-8 appearance-none rounded-lg border bg-background pl-8 pr-8 text-sm transition-colors hover:border-foreground/25 focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/20"
                  value={salaryPreset}
                  onChange={(e) => setSalaryPreset(Number(e.target.value))}
                >
                  {SALARY_PRESETS.map((p, i) => (
                    <option key={i} value={i}>
                      {p.label}
                    </option>
                  ))}
                </select>
                <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
              </div>

              <button
                aria-pressed={remoteOnly}
                onClick={() => setRemoteOnly(!remoteOnly)}
                className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
                  remoteOnly
                    ? "border-emerald-300 bg-emerald-50 text-emerald-700 dark:border-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"
                    : "border-border text-muted-foreground hover:bg-muted"
                }`}
              >
                <Wifi className="h-3 w-3" />
                Remote only
              </button>

              {hasFilters && (
                <Button
                  variant="ghost"
                  size="xs"
                  onClick={clearFilters}
                  className="text-muted-foreground"
                >
                  <X className="h-3 w-3" />
                  Clear
                </Button>
              )}

              <span className="ml-auto text-xs tabular-nums text-muted-foreground">
                {filteredRoles.length} role{filteredRoles.length !== 1 ? "s" : ""}
                {hasFilters ? " found" : ""}
              </span>
            </div>
          </Card>

          {/* Expand/Collapse */}
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">
              {grouped.length} categor{grouped.length !== 1 ? "ies" : "y"}
            </span>
            <div className="flex gap-1">
              <Button
                variant="ghost"
                size="xs"
                onClick={expandAll}
                className="text-muted-foreground"
              >
                Expand all
              </Button>
              <Button
                variant="ghost"
                size="xs"
                onClick={collapseAll}
                className="text-muted-foreground"
              >
                Collapse all
              </Button>
            </div>
          </div>

          {/* Role List */}
          {grouped.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-12 text-center">
              <FolderOpen className="mb-3 h-8 w-8 text-muted-foreground/50" />
              <p className="text-sm font-medium text-muted-foreground">
                No roles match your filters
              </p>
              <Button
                variant="link"
                size="xs"
                onClick={clearFilters}
                className="mt-1"
              >
                Clear all filters
              </Button>
            </div>
          ) : (
            <div className="space-y-2">
              {grouped.map(([category, categoryRoles]) => {
                const isExpanded = expandedCategories.has(category);
                return (
                  <div
                    key={category}
                    className="rounded-lg border bg-card overflow-hidden"
                  >
                    <button
                      aria-expanded={isExpanded}
                      onClick={() => toggleCategory(category)}
                      className="flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-muted/50 transition-colors"
                    >
                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
                      ) : (
                        <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
                      )}
                      <span className="font-medium text-sm">{category}</span>
                      <Badge variant="secondary" className="text-[10px] ml-auto">
                        {categoryRoles.length}
                      </Badge>
                    </button>
                    {isExpanded && (
                      <div className="border-t divide-y">
                        {categoryRoles.map((role) => (
                          <div
                            key={role.id}
                            className="px-4 py-3 pl-11 hover:bg-muted/30 transition-colors"
                          >
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="text-sm font-medium">
                                {role.title}
                              </span>
                              {role.seniority && (
                                <Badge
                                  variant="outline"
                                  className={`text-[10px] ${SENIORITY_COLORS[role.seniority] || ""}`}
                                >
                                  {role.seniority}
                                </Badge>
                              )}
                              {role.remote_friendly && (
                                <span className="inline-flex items-center gap-1 text-[10px] font-medium text-emerald-600 dark:text-emerald-400">
                                  <Wifi className="h-2.5 w-2.5" />
                                  Remote
                                </span>
                              )}
                            </div>
                            {(role.salary_min_ph || role.salary_max_ph) && (
                              <div className="mt-1 flex items-center gap-1">
                                <DollarSign className="h-3 w-3 text-emerald-600 dark:text-emerald-400" />
                                <span className="text-xs font-medium text-emerald-600 dark:text-emerald-400">
                                  {formatSalaryRange(
                                    role.salary_min_ph,
                                    role.salary_max_ph,
                                  )}
                                  /mo
                                </span>
                              </div>
                            )}
                            {role.description && (
                              <p className="mt-1 text-xs leading-relaxed text-muted-foreground line-clamp-2">
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
