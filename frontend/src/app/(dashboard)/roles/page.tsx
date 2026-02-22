"use client";

import { useState, useEffect, useMemo } from "react";
import { ChevronDown, ChevronRight, Briefcase } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { apiGet } from "@/lib/api-client";
import type { RoleListResponse, RoleResponse } from "@/types/career";

export default function RolesPage() {
  const [roles, setRoles] = useState<RoleResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(),
  );

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

  const grouped = useMemo(() => {
    const groups: Record<string, RoleResponse[]> = {};
    for (const role of roles) {
      const cat = role.category || "Other";
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(role);
    }
    return Object.entries(groups).sort(([a], [b]) => a.localeCompare(b));
  }, [roles]);

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

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Roles Overview</h2>
        <p className="text-muted-foreground">
          Browse all {roles.length} roles across {grouped.length} categories.
        </p>
      </div>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading roles...</p>
      ) : (
        <>
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

          <div className="space-y-3">
            {grouped.map(([category, categoryRoles]) => {
              const isExpanded = expandedCategories.has(category);
              return (
                <Card key={category}>
                  <button
                    onClick={() => toggleCategory(category)}
                    className="flex w-full items-center justify-between px-6 py-4 text-left hover:bg-muted/50 transition-colors rounded-t-lg"
                  >
                    <div className="flex items-center gap-3">
                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4 text-muted-foreground" />
                      ) : (
                        <ChevronRight className="h-4 w-4 text-muted-foreground" />
                      )}
                      <span className="font-semibold">{category}</span>
                      <Badge variant="secondary" className="text-xs">
                        {categoryRoles.length}
                      </Badge>
                    </div>
                  </button>
                  {isExpanded && (
                    <CardContent className="pt-0 pb-4">
                      <div className="grid gap-2 sm:grid-cols-2">
                        {categoryRoles.map((role) => (
                          <div
                            key={role.id}
                            className="flex items-start gap-2 rounded-md border px-3 py-2"
                          >
                            <Briefcase className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                            <div className="min-w-0">
                              <p className="text-sm font-medium">
                                {role.title}
                              </p>
                              {role.description && (
                                <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
                                  {role.description}
                                </p>
                              )}
                              <div className="flex flex-wrap items-center gap-1 mt-1">
                                {role.seniority && (
                                  <Badge
                                    variant="outline"
                                    className="text-[10px]"
                                  >
                                    {role.seniority}
                                  </Badge>
                                )}
                                {role.remote_friendly && (
                                  <Badge
                                    variant="outline"
                                    className="text-[10px]"
                                  >
                                    Remote
                                  </Badge>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  )}
                </Card>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
