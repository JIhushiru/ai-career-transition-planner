"use client";

import { ArrowRight, ArrowUp, ArrowDown, Clock, TrendingUp, ChevronRight, DollarSign } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import type { TransitionPathResponse } from "@/types/career";
import { formatSalaryRange } from "@/lib/salary";

interface TransitionPathViewProps {
  path: TransitionPathResponse;
  index: number;
}

function difficultyConfig(d: number) {
  if (d < 0.3)
    return {
      label: "Easy",
      className:
        "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300",
    };
  if (d < 0.6)
    return {
      label: "Moderate",
      className:
        "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300",
    };
  return {
    label: "Challenging",
    className:
      "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  };
}

export function TransitionPathView({ path, index }: TransitionPathViewProps) {
  const allRoles = [
    path.steps[0]?.from_role,
    ...path.steps.map((s) => s.to_role),
  ].filter(Boolean);

  const firstRole = path.steps[0]?.from_role;
  const lastRole = path.steps[path.steps.length - 1]?.to_role;
  const difficulty = difficultyConfig(path.total_difficulty);

  const startSalaryMid =
    firstRole?.salary_min_ph != null && firstRole?.salary_max_ph != null
      ? (firstRole.salary_min_ph + firstRole.salary_max_ph) / 2
      : null;
  const endSalaryMid =
    lastRole?.salary_min_ph != null && lastRole?.salary_max_ph != null
      ? (lastRole.salary_min_ph + lastRole.salary_max_ph) / 2
      : null;
  const salaryUp =
    startSalaryMid != null && endSalaryMid != null
      ? endSalaryMid >= startSalaryMid
      : null;

  return (
    <Card className="overflow-hidden">
      {/* ── Path header ── */}
      <CardHeader className="space-y-3 bg-muted/30 pb-4">
        <div className="space-y-1.5">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
            Path {index + 1}
          </span>

          {/* Visual breadcrumb: Role A › Role B › Role C */}
          <div className="flex flex-wrap items-center gap-1">
            {allRoles.map((role, i) => (
              <div key={i} className="flex items-center gap-1">
                <span
                  className={`text-sm font-semibold leading-snug ${
                    i === allRoles.length - 1
                      ? "text-primary"
                      : "text-foreground"
                  }`}
                >
                  {role.title}
                </span>
                {i < allRoles.length - 1 && (
                  <ChevronRight className="h-3.5 w-3.5 flex-shrink-0 text-muted-foreground" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Stats chips */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Timeline */}
          <span className="inline-flex items-center gap-1.5 rounded-full border bg-background px-3 py-1 text-xs font-medium">
            <Clock className="h-3 w-3 text-muted-foreground" />
            {path.total_months ?? "?"} months
          </span>

          {/* Difficulty */}
          <span
            className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${difficulty.className}`}
          >
            <TrendingUp className="h-3 w-3" />
            {difficulty.label}
          </span>

          {/* Target salary with direction indicator */}
          {lastRole?.salary_min_ph != null && (
            <span
              className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${
                salaryUp === false
                  ? "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300"
                  : "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300"
              }`}
            >
              {salaryUp === false ? (
                <ArrowDown className="h-3 w-3" />
              ) : (
                <ArrowUp className="h-3 w-3" />
              )}
              <DollarSign className="h-3 w-3 -ml-1" />
              {formatSalaryRange(lastRole.salary_min_ph, lastRole.salary_max_ph)}/mo
            </span>
          )}
        </div>
      </CardHeader>

      {/* ── Steps ── */}
      <CardContent className="pt-5">
        <div className="space-y-0">
          {path.steps.map((step, i) => {
            const stepDiff = difficultyConfig(step.difficulty);
            const isLast = i === path.steps.length - 1;
            return (
              <div key={i} className="relative flex gap-4">
                {/* Timeline column */}
                <div className="flex flex-col items-center">
                  <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full border-2 border-primary bg-primary/10 text-xs font-bold text-primary">
                    {i + 1}
                  </div>
                  {!isLast && (
                    <div className="my-1 min-h-[1.75rem] w-px flex-1 bg-border" />
                  )}
                </div>

                {/* Step body */}
                <div className={`flex-1 ${isLast ? "pb-0" : "pb-5"}`}>
                  {/* Transition title */}
                  <div className="mb-1.5 flex flex-wrap items-center gap-1.5">
                    <span className="text-sm text-muted-foreground">
                      {step.from_role.title}
                    </span>
                    <ArrowRight className="h-3.5 w-3.5 flex-shrink-0 text-muted-foreground" />
                    <span className="text-sm font-semibold text-foreground">
                      {step.to_role.title}
                    </span>
                  </div>

                  {/* Meta row */}
                  <div className="mb-2.5 flex flex-wrap items-center gap-2">
                    <span className="text-xs text-muted-foreground">
                      ~{step.months ?? "?"} months
                    </span>
                    <span
                      className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${stepDiff.className}`}
                    >
                      {stepDiff.label}
                    </span>
                    {step.to_role.salary_min_ph != null && (
                      <span className="text-xs font-medium text-emerald-600 dark:text-emerald-400">
                        {formatSalaryRange(
                          step.to_role.salary_min_ph,
                          step.to_role.salary_max_ph,
                        )}
                        /mo
                      </span>
                    )}
                  </div>

                  {/* Skills */}
                  {step.skills_needed.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {step.skills_needed.map((skill) => (
                        <Badge
                          key={skill}
                          className="border-0 bg-primary/10 text-[10px] font-medium text-primary hover:bg-primary/20"
                        >
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
