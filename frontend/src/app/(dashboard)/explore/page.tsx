"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { MatchCard } from "@/components/career/match-card";
import { apiPost, apiGet } from "@/lib/api-client";
import { useSession } from "@/context/session-context";
import type { MatchResultsResponse, CategoryCount } from "@/types/career";

const careerModes = [
  { value: "growth", label: "Growth", description: "Maximize career growth" },
  { value: "stability", label: "Stability", description: "Prioritize job security" },
  { value: "pivot", label: "Pivot", description: "Open to career changes" },
  { value: "late_career", label: "Late Career", description: "15+ years experience" },
];

export default function ExplorePage() {
  const { userId: sessionUserId } = useSession();
  const [userId, setUserId] = useState("");
  const [yearsExp, setYearsExp] = useState("");
  const [careerMode, setCareerMode] = useState("growth");
  const [useLlm, setUseLlm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<MatchResultsResponse | null>(null);
  const [categories, setCategories] = useState<CategoryCount[]>([]);

  useEffect(() => {
    if (sessionUserId && !userId) {
      setUserId(String(sessionUserId));
    }
  }, [sessionUserId]);

  useEffect(() => {
    async function loadCategories() {
      try {
        const cats = await apiGet<CategoryCount[]>("/roles/categories/list");
        setCategories(cats);
      } catch {
        // silently fail
      }
    }
    loadCategories();
  }, []);

  const handleMatch = async () => {
    if (!userId.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiPost<MatchResultsResponse>("/career/match", {
        user_id: parseInt(userId),
        career_mode: careerMode,
        years_experience: yearsExp ? parseInt(yearsExp) : null,
        use_llm: useLlm,
        top_k: 15,
      });
      setResults(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Matching failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Explore Careers</h2>
        <p className="text-muted-foreground">
          Discover matching roles ranked by the hybrid AI meta-model.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Run Career Matching
          </CardTitle>
          <CardDescription>
            {sessionUserId
              ? "Your resume is loaded. Configure options and find matching roles."
              : <>Upload a resume first on the <Link href="/resume" className="underline text-primary">Resume page</Link> to get started.</>}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs font-medium">User ID</label>
              <Input
                placeholder="e.g., 1"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium">
                Years of Experience
              </label>
              <Input
                placeholder="e.g., 5"
                type="number"
                value={yearsExp}
                onChange={(e) => setYearsExp(e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="mb-2 block text-xs font-medium">Career Mode</label>
            <div className="flex flex-wrap gap-2">
              {careerModes.map((mode) => (
                <Badge
                  key={mode.value}
                  variant={careerMode === mode.value ? "default" : "outline"}
                  className="cursor-pointer px-3 py-1"
                  onClick={() => setCareerMode(mode.value)}
                >
                  {mode.label}
                </Badge>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={useLlm}
                onChange={(e) => setUseLlm(e.target.checked)}
                className="rounded"
              />
              Enable LLM scoring (requires API key)
            </label>
          </div>

          <Button
            onClick={handleMatch}
            disabled={isLoading || !userId.trim()}
            className="w-full sm:w-auto"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Find Matching Careers
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {categories.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {categories.map((c) => (
            <Badge key={c.category} variant="secondary">
              {c.category}: {c.count}
            </Badge>
          ))}
        </div>
      )}

      {error && (
        <Card className="border-destructive">
          <CardContent className="py-4 text-sm text-destructive">
            {error}
          </CardContent>
        </Card>
      )}

      {results && (
        <div className="space-y-4">
          <h3 className="font-semibold">
            Top {results.matches.length} Matches
          </h3>
          <div className="grid gap-4 lg:grid-cols-2">
            {results.matches.map((match, i) => (
              <MatchCard key={match.role.id} match={match} rank={i + 1} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
