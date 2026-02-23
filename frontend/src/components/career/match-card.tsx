"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Check, X, TrendingUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { UserMatchResponse } from "@/types/career";
import { formatSalaryRange, formatSalaryDelta } from "@/lib/salary";
import { SENIORITY_COLORS } from "@/lib/constants";

function ScoreBar({ label, value }: { label: string; value: number | null }) {
  const pct = Math.round((value ?? 0) * 100);
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>{label}</span>
        <span>{pct}%</span>
      </div>
      <div className="h-1.5 rounded-full bg-muted">
        <div
          className="h-1.5 rounded-full bg-primary transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

interface MatchCardProps {
  match: UserMatchResponse;
  rank: number;
  onClick?: () => void;
}

export function MatchCard({ match, rank, onClick }: MatchCardProps) {
  const { role, meta_score, breakdown, explanation, matched_skills, missing_skills, salary_increase_pct, salary_increase_min, salary_increase_max } = match;
  const pct = Math.round(meta_score * 100);
  const [expanded, setExpanded] = useState(false);

  const hasSkillData = matched_skills.length > 0 || missing_skills.length > 0;
  const hasSalaryIncrease = salary_increase_pct != null && salary_increase_pct > 0;

  return (
    <Card
      className="transition-shadow hover:shadow-md"
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
                {rank}
              </span>
              <CardTitle className="text-base">{role.title}</CardTitle>
            </div>
            <CardDescription className="mt-1">
              {role.category}
              {role.seniority && (
                <Badge
                  variant="secondary"
                  className={`ml-2 text-[10px] ${SENIORITY_COLORS[role.seniority] || ""}`}
                >
                  {role.seniority}
                </Badge>
              )}
              {role.salary_range_ph && (
                <span className="ml-2 text-xs">{role.salary_range_ph}</span>
              )}
              {hasSalaryIncrease && (
                <span className="block mt-1 text-xs font-medium text-emerald-600 dark:text-emerald-400">
                  {formatSalaryDelta(salary_increase_min!)} to {formatSalaryDelta(salary_increase_max!)}/mo
                </span>
              )}
            </CardDescription>
          </div>
          <div className="text-right space-y-1">
            <span className="text-2xl font-bold text-primary">{pct}%</span>
            <p className="text-[10px] text-muted-foreground">match</p>
            {hasSalaryIncrease && (
              <Badge className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300 text-[10px]">
                <TrendingUp className="mr-0.5 h-3 w-3" />
                +{Math.round(salary_increase_pct!)}%
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-2 gap-x-4 gap-y-2">
          <ScoreBar label="Semantic Fit" value={breakdown.embedding_score} />
          <ScoreBar label="Skill Match" value={breakdown.skill_overlap_score} />
          <ScoreBar label="Experience" value={breakdown.experience_match_score} />
          <ScoreBar label="Market Demand" value={breakdown.market_score} />
        </div>
        {explanation && (
          <p className="text-xs text-muted-foreground">{explanation}</p>
        )}

        {hasSkillData && (
          <>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                setExpanded(!expanded);
              }}
              className="flex w-full items-center justify-center gap-1 rounded-md border py-1.5 text-xs text-muted-foreground transition-colors hover:bg-muted"
            >
              {expanded ? (
                <>Hide Skill Gap <ChevronUp className="h-3 w-3" /></>
              ) : (
                <>
                  Show Skill Gap
                  {missing_skills.length > 0 && (
                    <Badge variant="secondary" className="ml-1 text-[10px] px-1.5 py-0">
                      {missing_skills.length} to learn
                    </Badge>
                  )}
                  <ChevronDown className="h-3 w-3" />
                </>
              )}
            </button>

            {expanded && (
              <div className="space-y-3 rounded-md border bg-muted/30 p-3">
                {matched_skills.length > 0 && (
                  <div>
                    <p className="mb-1.5 text-xs font-medium text-green-600 dark:text-green-400">
                      Skills you have ({matched_skills.length})
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {matched_skills.map((skill) => (
                        <Badge
                          key={skill}
                          variant="secondary"
                          className="bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 text-[10px]"
                        >
                          <Check className="mr-0.5 h-2.5 w-2.5" />
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                {missing_skills.length > 0 && (
                  <div>
                    <p className="mb-1.5 text-xs font-medium text-amber-600 dark:text-amber-400">
                      Skills to develop ({missing_skills.length})
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {missing_skills.map((skill) => (
                        <Badge
                          key={skill}
                          variant="secondary"
                          className="bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300 text-[10px]"
                        >
                          <X className="mr-0.5 h-2.5 w-2.5" />
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
