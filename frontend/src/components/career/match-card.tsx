"use client";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { UserMatchResponse } from "@/types/career";

const seniorityColors: Record<string, string> = {
  entry: "bg-green-100 text-green-700",
  mid: "bg-blue-100 text-blue-700",
  senior: "bg-purple-100 text-purple-700",
  lead: "bg-orange-100 text-orange-700",
  executive: "bg-red-100 text-red-700",
};

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
  const { role, meta_score, breakdown, explanation } = match;
  const pct = Math.round(meta_score * 100);

  return (
    <Card
      className={`cursor-pointer transition-shadow hover:shadow-md ${onClick ? "" : ""}`}
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
                  className={`ml-2 text-[10px] ${seniorityColors[role.seniority] || ""}`}
                >
                  {role.seniority}
                </Badge>
              )}
              {role.salary_range_ph && (
                <span className="ml-2 text-xs">{role.salary_range_ph}</span>
              )}
            </CardDescription>
          </div>
          <div className="text-right">
            <span className="text-2xl font-bold text-primary">{pct}%</span>
            <p className="text-[10px] text-muted-foreground">match</p>
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
      </CardContent>
    </Card>
  );
}
