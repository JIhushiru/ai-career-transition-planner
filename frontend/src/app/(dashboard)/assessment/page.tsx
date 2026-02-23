"use client";

import { useState, useEffect } from "react";
import {
  Loader2,
  ClipboardCheck,
  CheckCircle2,
  Send,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { RolePicker } from "@/components/career/role-picker";
import { apiGet, apiPost } from "@/lib/api-client";
import { useSession } from "@/context/session-context";
import type { AssessmentQuestionsResponse } from "@/types/career";

const RATING_LABELS: Record<number, string> = {
  0: "No experience",
  1: "Beginner",
  2: "Intermediate",
  3: "Advanced",
  4: "Expert",
};

const RATING_COLORS: Record<number, string> = {
  0: "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
  1: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  2: "bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400",
  3: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  4: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
};

export default function AssessmentPage() {
  const { userId: sessionUserId } = useSession();
  const [targetRoleId, setTargetRoleId] = useState<number | null>(null);
  const [questions, setQuestions] = useState<
    AssessmentQuestionsResponse | null
  >(null);
  const [ratings, setRatings] = useState<Record<string, number>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<{
    added: number;
    updated: number;
    total: number;
  } | null>(null);

  const loadQuestions = async () => {
    setIsLoading(true);
    setError(null);
    setSubmitted(false);
    setResult(null);
    try {
      const params = targetRoleId
        ? `?target_role_id=${targetRoleId}`
        : "";
      const res = await apiGet<AssessmentQuestionsResponse>(
        `/career/assessment/questions${params}`
      );
      setQuestions(res);
      // Initialize ratings to 0
      const initial: Record<string, number> = {};
      for (const q of res.questions) {
        initial[q.skill] = 0;
      }
      setRatings(initial);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load questions"
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadQuestions();
  }, [targetRoleId]);

  const handleSubmit = async () => {
    if (!sessionUserId) return;
    setIsSubmitting(true);
    setError(null);
    try {
      const ratingsList = Object.entries(ratings)
        .filter(([, r]) => r > 0)
        .map(([skill, rating]) => ({ skill, rating }));

      if (ratingsList.length === 0) {
        setError("Please rate at least one skill before submitting.");
        setIsSubmitting(false);
        return;
      }

      const res = await apiPost<{ added: number; updated: number; total: number }>(
        "/career/assessment",
        {
          user_id: sessionUserId,
          ratings: ratingsList,
        }
      );
      setResult(res);
      setSubmitted(true);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to submit assessment"
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const ratedCount = Object.values(ratings).filter((r) => r > 0).length;
  const totalCount = questions?.questions.length || 0;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <ClipboardCheck className="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
          Skill Self-Assessment
        </h2>
        <p className="text-muted-foreground">
          Rate your skills to improve career matching accuracy. This supplements
          skills extracted from your resume.
        </p>
      </div>

      {/* Target Role Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Assessment Focus (Optional)
          </CardTitle>
          <CardDescription>
            Select a target role to get questions tailored to that role, or
            leave empty for a general assessment.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <RolePicker
            selectedRoleId={targetRoleId}
            onSelect={(id) => {
              setTargetRoleId(id);
              setSubmitted(false);
            }}
          />
        </CardContent>
      </Card>

      {error && (
        <Card className="border-destructive">
          <CardContent role="alert" className="py-4 text-sm text-destructive">
            {error}
          </CardContent>
        </Card>
      )}

      {submitted && result && (
        <Card className="border-green-200 bg-green-50/50 dark:border-green-800 dark:bg-green-950/20">
          <CardContent className="py-4 flex items-center gap-3">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            <div>
              <p className="font-medium text-green-800 dark:text-green-400">
                Assessment saved successfully!
              </p>
              <p className="text-sm text-green-600 dark:text-green-500">
                {result.added} new skills added, {result.updated} skills updated
                ({result.total} total).
                Your career matches will now be more accurate.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {isLoading && (
        <Card>
          <CardContent className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </CardContent>
        </Card>
      )}

      {!isLoading && questions && questions.questions.length > 0 && (
        <>
          {/* Progress */}
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">
              {ratedCount} of {totalCount} skills rated
            </span>
            <div className="w-48 h-2 rounded-full bg-muted overflow-hidden">
              <div
                className="h-full bg-emerald-500 transition-all"
                style={{
                  width: `${
                    totalCount > 0 ? (ratedCount / totalCount) * 100 : 0
                  }%`,
                }}
              />
            </div>
          </div>

          {/* Questions */}
          <div className="space-y-2">
            {questions.questions.map((q) => (
              <Card key={q.skill} className="overflow-hidden">
                <div className="flex items-center justify-between px-4 py-3">
                  <div className="flex items-center gap-3">
                    <span className="font-medium text-sm">{q.skill}</span>
                    {q.importance === "required" && (
                      <span className="rounded bg-red-100 px-1.5 py-0.5 text-[10px] text-red-600 dark:bg-red-900/30 dark:text-red-400">
                        Required
                      </span>
                    )}
                    {q.importance === "preferred" && (
                      <span className="rounded bg-yellow-100 px-1.5 py-0.5 text-[10px] text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400">
                        Preferred
                      </span>
                    )}
                  </div>
                  <div role="group" aria-label={`Rate ${q.skill}`} className="flex items-center gap-1">
                    {[0, 1, 2, 3, 4].map((level) => (
                      <button
                        key={level}
                        onClick={() =>
                          setRatings((prev) => ({
                            ...prev,
                            [q.skill]: level,
                          }))
                        }
                        aria-pressed={ratings[q.skill] === level}
                        className={`rounded px-2 py-1 text-xs transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                          ratings[q.skill] === level
                            ? RATING_COLORS[level]
                            : "bg-muted/50 text-muted-foreground hover:bg-muted"
                        }`}
                        title={RATING_LABELS[level]}
                      >
                        {RATING_LABELS[level]}
                      </button>
                    ))}
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Submit */}
          <div className="flex justify-end">
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting || ratedCount === 0 || !sessionUserId}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Send className="mr-2 h-4 w-4" />
                  Submit Assessment ({ratedCount} skills)
                </>
              )}
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
