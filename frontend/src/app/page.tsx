"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  FileText,
  Tags,
  Compass,
  Route,
  GraduationCap,
  TrendingUp,
  ArrowRight,
} from "lucide-react";
import { apiGet } from "@/lib/api-client";
import { formatPHP, formatSalaryRange } from "@/lib/salary";
import type { UserMatchResponse, MatchResultsResponse } from "@/types/career";

const features = [
  {
    icon: FileText,
    title: "Upload Resume",
    description:
      "Upload your resume to discover your earning potential and find roles that pay more.",
    href: "/resume",
    color: "text-blue-600 dark:text-blue-400",
  },
  {
    icon: Compass,
    title: "Find Higher-Paying Roles",
    description:
      "AI-powered matching finds roles that fit your skills and pay more than your current salary.",
    href: "/explore",
    color: "text-violet-600 dark:text-violet-400",
  },
  {
    icon: Route,
    title: "Map Your Path",
    description:
      "See step-by-step career transitions with salary at each stage, from where you are to where you want to be.",
    href: "/transitions",
    color: "text-emerald-600 dark:text-emerald-400",
  },
  {
    icon: GraduationCap,
    title: "Build Your Roadmap",
    description:
      "Get a personalized learning plan to close skill gaps and unlock higher-salary roles.",
    href: "/roadmap",
    color: "text-amber-600 dark:text-amber-400",
  },
];

function QuickWinCard({ match, rank }: { match: UserMatchResponse; rank: number }) {
  const { role, meta_score, salary_increase_pct } = match;
  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-xs font-bold text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300">
                {rank}
              </span>
              <span className="font-medium text-sm">{role.title}</span>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">{role.category}</p>
            {role.salary_min_ph && (
              <p className="mt-1 text-xs text-emerald-600 dark:text-emerald-400 font-medium">
                {formatSalaryRange(role.salary_min_ph, role.salary_max_ph)}/mo
              </p>
            )}
          </div>
          <div className="text-right">
            {salary_increase_pct != null && salary_increase_pct > 0 && (
              <Badge className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300">
                <TrendingUp className="mr-0.5 h-3 w-3" />
                +{Math.round(salary_increase_pct)}%
              </Badge>
            )}
            <p className="mt-1 text-xs text-muted-foreground">{Math.round(meta_score * 100)}% match</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function Home() {
  const [quickWins, setQuickWins] = useState<UserMatchResponse[]>([]);
  const [topSalary, setTopSalary] = useState<number | null>(null);
  const [currentSalary, setCurrentSalary] = useState<number | null>(null);
  const [hasData, setHasData] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("ct_token");
    const userId = localStorage.getItem("ct_user_id");
    const salary = localStorage.getItem("ct_current_salary");

    if (!token || !userId) return;

    if (salary) setCurrentSalary(parseInt(salary));

    // Try to load quick wins
    apiGet<UserMatchResponse[]>(`/career/quick-wins/${userId}`)
      .then((wins) => {
        if (wins.length > 0) {
          setQuickWins(wins);
          setHasData(true);
          // Find highest salary role
          const maxSalary = Math.max(
            ...wins
              .map((w) => w.role.salary_max_ph ?? 0)
              .filter((s) => s > 0),
          );
          if (maxSalary > 0) setTopSalary(maxSalary);
        }
      })
      .catch(() => {});

    // Fallback: load cached matches if no quick wins
    apiGet<MatchResultsResponse>(`/career/match/${userId}/results`)
      .then((res) => {
        if (res.matches.length > 0) {
          setHasData(true);
          if (!topSalary) {
            const maxSalary = Math.max(
              ...res.matches
                .map((m) => m.role.salary_max_ph ?? 0)
                .filter((s) => s > 0),
            );
            if (maxSalary > 0) setTopSalary(maxSalary);
          }
        }
      })
      .catch(() => {});
  }, []);

  const salaryIncreasePct =
    currentSalary && topSalary
      ? Math.round(((topSalary - currentSalary) / currentSalary) * 100)
      : null;

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto max-w-5xl px-6 py-16">
        {/* Hero */}
        <div className="mb-12 text-center">
          {hasData && topSalary && currentSalary && salaryIncreasePct && salaryIncreasePct > 0 ? (
            <>
              <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-emerald-100 dark:bg-emerald-900 px-4 py-2 text-sm font-medium text-emerald-700 dark:text-emerald-300">
                <TrendingUp className="h-4 w-4" />
                You could earn up to {salaryIncreasePct}% more
              </div>
              <h1 className="mb-4 text-4xl font-bold tracking-tight">
                Your skills could earn up to{" "}
                <span className="text-emerald-600 dark:text-emerald-400">
                  {formatPHP(topSalary)}/mo
                </span>
              </h1>
              <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
                That&apos;s{" "}
                <span className="font-semibold text-emerald-600 dark:text-emerald-400">
                  {formatPHP(topSalary - currentSalary)} more
                </span>{" "}
                than your current salary. Explore the roles that match your
                skills and pay more.
              </p>
            </>
          ) : (
            <>
              <h1 className="mb-4 text-4xl font-bold tracking-tight">
                Discover How Much More You Could Earn
              </h1>
              <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
                Upload your resume, enter your current salary, and our AI will
                find roles that match your skills and pay more. Your next
                career move starts here.
              </p>
            </>
          )}
          <div className="mt-6 flex justify-center gap-3">
            <Button asChild size="lg" className="bg-emerald-600 hover:bg-emerald-700 text-white">
              <Link href={hasData ? "/explore" : "/resume"}>
                {hasData ? "Explore Higher-Paying Roles" : "Get Started"}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>

        {/* Quick Wins */}
        {quickWins.length > 0 && (
          <div className="mb-12">
            <h2 className="mb-4 text-xl font-bold">
              Quick Wins — Roles You Can Reach That Pay More
            </h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {quickWins.slice(0, 3).map((win, i) => (
                <QuickWinCard key={win.role.id} match={win} rank={i + 1} />
              ))}
            </div>
            <div className="mt-4 text-center">
              <Button variant="outline" size="sm" asChild>
                <Link href="/explore">See all matches</Link>
              </Button>
            </div>
          </div>
        )}

        {/* Feature Cards */}
        <div className="grid gap-6 sm:grid-cols-2">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card key={feature.title} className="transition-shadow hover:shadow-md">
                <CardHeader>
                  <div className="mb-2 flex items-center gap-2">
                    <Icon className={`h-5 w-5 ${feature.color}`} />
                    <CardTitle className="text-base">{feature.title}</CardTitle>
                  </div>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" size="sm" asChild>
                    <Link href={feature.href}>
                      Open
                      <ArrowRight className="ml-1 h-3 w-3" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </main>
  );
}
