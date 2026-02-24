"use client";

import { ArrowRight, Clock, TrendingUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { TransitionPathResponse } from "@/types/career";
import { formatSalaryRange } from "@/lib/salary";

interface TransitionPathViewProps {
  path: TransitionPathResponse;
  index: number;
}

function difficultyColor(d: number): string {
  if (d < 0.3) return "text-green-600 dark:text-green-300";
  if (d < 0.6) return "text-yellow-600 dark:text-yellow-300";
  return "text-red-600 dark:text-red-300";
}

function difficultyLabel(d: number): string {
  if (d < 0.3) return "Easy";
  if (d < 0.6) return "Moderate";
  return "Challenging";
}

export function TransitionPathView({ path, index }: TransitionPathViewProps) {
  const firstRole = path.steps[0]?.from_role;
  const lastRole = path.steps[path.steps.length - 1]?.to_role;
  const startSalary = firstRole?.salary_min_ph || firstRole?.salary_max_ph;
  const endSalary = lastRole?.salary_min_ph || lastRole?.salary_max_ph;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">
            Path {index + 1}
          </CardTitle>
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {path.total_months ?? "?"} months
            </span>
            <span
              className={`flex items-center gap-1 ${difficultyColor(path.total_difficulty)}`}
            >
              <TrendingUp className="h-3 w-3" />
              {difficultyLabel(path.total_difficulty)}
            </span>
          </div>
        </div>
        {startSalary && endSalary && (
          <p className="text-xs text-emerald-600 dark:text-emerald-300">
            {formatSalaryRange(firstRole.salary_min_ph, firstRole.salary_max_ph)} → {formatSalaryRange(lastRole.salary_min_ph, lastRole.salary_max_ph)}/mo
          </p>
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {path.steps.map((step, i) => (
            <div key={i} className="flex items-start gap-3">
              <div className="flex flex-col items-center">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
                  {i + 1}
                </div>
                {i < path.steps.length - 1 && (
                  <div className="my-1 h-8 w-px bg-border" />
                )}
              </div>
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2 text-sm">
                  <span className="font-medium">{step.from_role.title}</span>
                  <ArrowRight className="h-3 w-3 text-muted-foreground" />
                  <span className="font-medium text-primary">
                    {step.to_role.title}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>~{step.months ?? "?"} months</span>
                  <span className={difficultyColor(step.difficulty)}>
                    {difficultyLabel(step.difficulty)}
                  </span>
                  {step.to_role.salary_min_ph && (
                    <span className="text-emerald-600 dark:text-emerald-300">
                      {formatSalaryRange(step.to_role.salary_min_ph, step.to_role.salary_max_ph)}/mo
                    </span>
                  )}
                </div>
                {step.skills_needed.length > 0 && (
                  <div className="flex flex-wrap gap-1 pt-1">
                    {step.skills_needed.map((skill) => (
                      <Badge
                        key={skill}
                        variant="outline"
                        className="text-[10px]"
                      >
                        {skill}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
