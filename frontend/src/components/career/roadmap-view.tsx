"use client";

import { CheckCircle2, Circle, Clock, BookOpen } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { RoadmapResponse, SkillGap, Milestone } from "@/types/career";
import { formatSalaryRange } from "@/lib/salary";

const priorityStyles: Record<string, string> = {
  high: "border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300",
  medium: "border-yellow-200 bg-yellow-50 text-yellow-700 dark:border-yellow-900 dark:bg-yellow-950 dark:text-yellow-300",
  low: "border-green-200 bg-green-50 text-green-700 dark:border-green-900 dark:bg-green-950 dark:text-green-300",
};

function SkillGapCard({ gap }: { gap: SkillGap }) {
  return (
    <div
      className={`rounded-lg border p-3 ${priorityStyles[gap.priority] || ""}`}
    >
      <div className="flex items-center justify-between">
        <span className="font-medium">{gap.skill}</span>
        <Badge variant="outline" className="text-[10px]">
          {gap.priority}
        </Badge>
      </div>
      {gap.estimated_hours && (
        <p className="mt-1 flex items-center gap-1 text-xs opacity-75">
          <Clock className="h-3 w-3" />
          ~{gap.estimated_hours} hours
        </p>
      )}
      {gap.resources.length > 0 && (
        <div className="mt-2 space-y-1">
          {gap.resources.map((r, i) => (
            <p key={i} className="flex items-start gap-1 text-[11px]">
              <BookOpen className="mt-0.5 h-3 w-3 shrink-0" />
              {r.url ? (
                <a
                  href={r.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline hover:opacity-80"
                  onClick={(e) => e.stopPropagation()}
                >
                  {r.title}
                </a>
              ) : (
                <span>{r.title}</span>
              )}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

function MilestoneCard({
  milestone,
  isLast,
}: {
  milestone: Milestone;
  isLast: boolean;
}) {
  return (
    <div className="flex gap-3">
      <div className="flex flex-col items-center">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
          {milestone.phase}
        </div>
        {!isLast && <div className="my-1 h-full w-px bg-border" />}
      </div>
      <div className="flex-1 pb-6">
        <h4 className="font-medium">{milestone.title}</h4>
        <p className="text-sm text-muted-foreground">
          {milestone.description}
        </p>
        <div className="mt-2 flex items-center gap-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {milestone.estimated_hours}h / ~{milestone.estimated_weeks} weeks
          </span>
        </div>
        {milestone.skills.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {milestone.skills.map((s) => (
              <Badge key={s} variant="secondary" className="text-[10px]">
                {s}
              </Badge>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface RoadmapViewProps {
  roadmap: RoadmapResponse;
}

export function RoadmapView({ roadmap }: RoadmapViewProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            Roadmap to {roadmap.target_role.title}
          </CardTitle>
          <CardDescription>
            {roadmap.skill_gaps.length} skill gaps &middot;{" "}
            {roadmap.total_estimated_hours ?? "?"}h estimated learning
            {roadmap.target_role.salary_min_ph && (
              <span className="block mt-1 text-emerald-600 dark:text-emerald-400 font-medium">
                Target salary: {formatSalaryRange(roadmap.target_role.salary_min_ph, roadmap.target_role.salary_max_ph)}/mo
              </span>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {roadmap.milestones.map((m, i) => (
              <MilestoneCard
                key={m.phase}
                milestone={m}
                isLast={i === roadmap.milestones.length - 1}
              />
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Skill Gaps</CardTitle>
          <CardDescription>
            Skills you need to develop, sorted by priority
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2">
            {roadmap.skill_gaps.map((gap) => (
              <SkillGapCard key={gap.skill} gap={gap} />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
