"use client";

import { useState, useEffect } from "react";
import { Loader2, Search } from "lucide-react";
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
import { ResumePicker } from "@/components/resume/resume-picker";
import { apiPost, apiPut } from "@/lib/api-client";
import { safeParseInt, STORAGE_KEYS, cacheResult, loadCachedResult } from "@/lib/constants";
import { useSession } from "@/context/session-context";
import type { MatchResultsResponse } from "@/types/career";
import type { ResumeListItem } from "@/types/resume";

const careerModes = [
  { value: "maximize_earnings", label: "Maximize Earnings", description: "Find higher-paying roles" },
  { value: "growth", label: "Growth", description: "Maximize career growth" },
  { value: "stability", label: "Stability", description: "Prioritize job security" },
  { value: "pivot", label: "Pivot", description: "Open to career changes" },
  { value: "late_career", label: "Late Career", description: "15+ years experience" },
];

export default function ExplorePage() {
  const { userId: sessionUserId, currentSalary, setCurrentSalary } = useSession();
  const [selectedResumeId, setSelectedResumeId] = useState<number | null>(null);
  const [yearsExp, setYearsExp] = useState("");
  const [salaryInput, setSalaryInput] = useState(currentSalary ? String(currentSalary) : "");
  const [careerMode, setCareerMode] = useState("maximize_earnings");
  const [useLlm, setUseLlm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<MatchResultsResponse | null>(null);

  // Restore cached results on mount
  useEffect(() => {
    const cached = loadCachedResult<MatchResultsResponse>(STORAGE_KEYS.CACHE_EXPLORE);
    if (cached) setResults(cached);
  }, []);

  const handleResumeSelect = (resume: ResumeListItem) => {
    setSelectedResumeId(resume.id);
  };

  const handleMatch = async () => {
    if (!sessionUserId) return;
    setIsLoading(true);
    setError(null);
    try {
      const parsedSalary = safeParseInt(salaryInput);

      // Save salary to session and backend profile
      if (parsedSalary && parsedSalary !== currentSalary) {
        setCurrentSalary(parsedSalary);
        apiPut("/auth/me/profile", { current_salary: parsedSalary }).catch(() => {
          // Profile update is best-effort — salary is still used locally
        });
      }

      const res = await apiPost<MatchResultsResponse>("/career/match", {
        user_id: sessionUserId,
        resume_id: selectedResumeId ?? undefined,
        career_mode: careerMode,
        years_experience: safeParseInt(yearsExp),
        current_salary: parsedSalary,
        use_llm: useLlm,
        top_k: 15,
      });
      setResults(res);
      cacheResult(STORAGE_KEYS.CACHE_EXPLORE, res);
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
            Select a resume and configure options to find matching roles.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <ResumePicker
              selectedResumeId={selectedResumeId}
              onSelect={handleResumeSelect}
            />
            <div>
              <label htmlFor="explore-salary" className="mb-1 block text-sm font-medium">
                Current Monthly Salary (PHP)
              </label>
              <Input
                id="explore-salary"
                placeholder="e.g., 25000"
                type="number"
                value={salaryInput}
                onChange={(e) => setSalaryInput(e.target.value)}
              />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="explore-years" className="mb-1 block text-sm font-medium">
                Years of Experience
              </label>
              <Input
                id="explore-years"
                placeholder="e.g., 5"
                type="number"
                value={yearsExp}
                onChange={(e) => setYearsExp(e.target.value)}
              />
            </div>
          </div>

          <div>
            <label id="career-mode-label" className="mb-2 block text-sm font-medium">Career Mode</label>
            <div role="radiogroup" aria-labelledby="career-mode-label" className="flex flex-wrap gap-2">
              {careerModes.map((mode) => (
                <Badge
                  key={mode.value}
                  role="radio"
                  aria-checked={careerMode === mode.value}
                  tabIndex={0}
                  variant={careerMode === mode.value ? "default" : "outline"}
                  className="cursor-pointer px-3 py-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  onClick={() => setCareerMode(mode.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      setCareerMode(mode.value);
                    }
                  }}
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
                className="h-4 w-4 rounded border-input accent-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
              Enable LLM scoring
            </label>
          </div>

          <Button
            onClick={handleMatch}
            disabled={isLoading || !sessionUserId || !selectedResumeId}
            className="w-full sm:w-auto"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Search className="mr-2 h-4 w-4" />
                Find Matching Careers
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {error && (
        <Card className="border-destructive">
          <CardContent role="alert" className="py-4 text-sm text-destructive">
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
