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
  Compass,
  Route,
  GraduationCap,
  TrendingUp,
  ArrowRight,
  Star,
  ClipboardCheck,
  CheckCircle2,
  Target,
} from "lucide-react";
import { apiGet } from "@/lib/api-client";
import { STORAGE_KEYS } from "@/lib/constants";
import { formatSalaryRange } from "@/lib/salary";
import type { UserMatchResponse, MatchResultsResponse } from "@/types/career";

const MOTIVATIONAL_QUOTES = [
  { text: "The only way to do great work is to love what you do.", author: "Steve Jobs" },
  { text: "Your career is a marathon, not a sprint. Every skill you build compounds.", author: "Unknown" },
  { text: "The best time to plant a tree was 20 years ago. The second best time is now.", author: "Chinese Proverb" },
  { text: "Success is not final, failure is not fatal: it is the courage to continue that counts.", author: "Winston Churchill" },
  { text: "Don't watch the clock; do what it does. Keep going.", author: "Sam Levenson" },
];

const features = [
  {
    icon: FileText,
    title: "Upload Resume",
    description:
      "Upload your resume to discover your earning potential and find roles that pay more.",
    href: "/resume",
    iconColor: "text-blue-600 dark:text-blue-400",
    bgColor: "bg-blue-100 dark:bg-blue-950",
  },
  {
    icon: Compass,
    title: "Find Higher-Paying Roles",
    description:
      "AI-powered matching finds roles that fit your skills and pay more than your current salary.",
    href: "/explore",
    iconColor: "text-violet-600 dark:text-violet-400",
    bgColor: "bg-violet-100 dark:bg-violet-950",
  },
  {
    icon: Route,
    title: "Map Your Path",
    description:
      "See step-by-step career transitions with salary at each stage, from where you are to where you want to be.",
    href: "/transitions",
    iconColor: "text-emerald-600 dark:text-emerald-400",
    bgColor: "bg-emerald-100 dark:bg-emerald-950",
  },
  {
    icon: GraduationCap,
    title: "Build Your Roadmap",
    description:
      "Get a personalized learning plan to close skill gaps and unlock higher-salary roles.",
    href: "/roadmap",
    iconColor: "text-amber-600 dark:text-amber-400",
    bgColor: "bg-amber-100 dark:bg-amber-950",
  },
  {
    icon: Star,
    title: "Dream Job Planner",
    description:
      "Pick your dream role and get a reverse-engineered plan with career paths, weekly actions, and interview prep.",
    href: "/dream-job",
    iconColor: "text-amber-500 dark:text-amber-400",
    bgColor: "bg-amber-100 dark:bg-amber-950",
  },
  {
    icon: ClipboardCheck,
    title: "Self-Assessment",
    description:
      "Rate your own skill levels to improve match accuracy and get better recommendations.",
    href: "/assessment",
    iconColor: "text-pink-600 dark:text-pink-400",
    bgColor: "bg-pink-100 dark:bg-pink-950",
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

interface SkillsSummary {
  skills: { name: string; category: string }[];
  categories: Record<string, { name: string }[]>;
}

function ProgressSummary({
  skillCount,
  matchCount,
  topCategory,
}: {
  skillCount: number;
  matchCount: number;
  topCategory: string | null;
}) {
  const steps = [
    { label: "Resume uploaded", done: skillCount > 0 },
    { label: "Skills extracted", done: skillCount > 0 },
    { label: "Roles matched", done: matchCount > 0 },
  ];
  const completed = steps.filter((s) => s.done).length;

  return (
    <Card className="mb-8">
      <CardContent className="py-5">
        <div className="grid gap-4 sm:grid-cols-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-primary">{skillCount}</p>
            <p className="text-xs text-muted-foreground">Skills Detected</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-violet-600 dark:text-violet-400">{matchCount}</p>
            <p className="text-xs text-muted-foreground">Roles Matched</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">
              {topCategory || "\u2014"}
            </p>
            <p className="text-xs text-muted-foreground">Top Skill Area</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
              {completed}/{steps.length}
            </p>
            <p className="text-xs text-muted-foreground">Steps Completed</p>
          </div>
        </div>

        <div className="mt-4 flex items-center gap-3">
          {steps.map((step) => (
            <div key={step.label} className="flex items-center gap-1.5 text-xs">
              {step.done ? (
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
              ) : (
                <Target className="h-3.5 w-3.5 text-muted-foreground" />
              )}
              <span className={step.done ? "text-foreground" : "text-muted-foreground"}>
                {step.label}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default function Home() {
  const [quickWins, setQuickWins] = useState<UserMatchResponse[]>([]);
  const [hasData, setHasData] = useState(false);
  const [skillCount, setSkillCount] = useState(0);
  const [matchCount, setMatchCount] = useState(0);
  const [topCategory, setTopCategory] = useState<string | null>(null);
  const [quote] = useState(() => MOTIVATIONAL_QUOTES[Math.floor(Math.random() * MOTIVATIONAL_QUOTES.length)]);

  useEffect(() => {
    const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
    const userId = localStorage.getItem(STORAGE_KEYS.USER_ID);
    const resumeId = localStorage.getItem(STORAGE_KEYS.RESUME_ID);

    if (!token || !userId) return;

    // Load skill stats if we have a resume
    if (resumeId) {
      apiGet<SkillsSummary>(`/resume/${resumeId}/skills`)
        .then((data) => {
          setSkillCount(data.skills.length);
          const cats = Object.entries(data.categories);
          if (cats.length > 0) {
            const sorted = cats.sort((a, b) => b[1].length - a[1].length);
            setTopCategory(sorted[0][0]);
          }
        })
        .catch(() => {
          // Dashboard data is optional — user hasn't uploaded a resume yet
        });
    }

    // Try to load quick wins (optional — only populated after matching)
    apiGet<UserMatchResponse[]>(`/career/quick-wins/${userId}`)
      .then((wins) => {
        if (wins.length > 0) {
          setQuickWins(wins);
          setHasData(true);
        }
      })
      .catch(() => {
        // No matches computed yet — this is expected for new users
      });

    // Load cached matches (optional — only populated after matching)
    apiGet<MatchResultsResponse>(`/career/match/${userId}/results`)
      .then((res) => {
        if (res.matches.length > 0) {
          setHasData(true);
          setMatchCount(res.matches.length);
        }
      })
      .catch(() => {
        // No cached results — this is expected for new users
      });
  }, []);

  return (
    <div className="mx-auto max-w-5xl py-10">
      {/* Hero */}
      <div className="mb-12 text-center">
        <h1 className="mb-4 text-4xl font-bold tracking-tight">
          Plan Your Next Career Move
        </h1>
        <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
          Upload your resume, discover roles that match your skills, and build
          a personalized roadmap to reach your dream job.
        </p>
        <blockquote className="mx-auto mt-6 max-w-xl border-l-4 border-primary/30 pl-4 text-left">
          <p className="italic text-muted-foreground">
            &ldquo;{quote.text}&rdquo;
          </p>
          <footer className="mt-1 text-xs text-muted-foreground/70">
            &mdash; {quote.author}
          </footer>
        </blockquote>
        <div className="mt-6 flex justify-center gap-3">
          <Button asChild size="lg">
            <Link href={hasData ? "/explore" : "/resume"}>
              {hasData ? "Explore Matching Roles" : "Get Started"}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </div>

      {/* Progress Summary */}
      {(skillCount > 0 || matchCount > 0) && (
        <ProgressSummary
          skillCount={skillCount}
          matchCount={matchCount}
          topCategory={topCategory}
        />
      )}

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
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <Link key={feature.title} href={feature.href} className="group rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
              <Card className="h-full transition-all hover:shadow-md group-hover:border-primary/20">
                <CardHeader>
                  <div className={`mb-3 inline-flex h-10 w-10 items-center justify-center rounded-lg ${feature.bgColor}`}>
                    <Icon className={`h-5 w-5 ${feature.iconColor}`} />
                  </div>
                  <CardTitle className="text-base">{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <span className="inline-flex items-center text-sm font-medium text-primary group-hover:underline">
                    Open
                    <ArrowRight className="ml-1 h-3 w-3 transition-transform group-hover:translate-x-0.5" />
                  </span>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
