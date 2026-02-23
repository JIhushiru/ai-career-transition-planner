"use client";

import { useState } from "react";
import { Loader2, Navigation } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { TransitionPathView } from "@/components/career/transition-path";
import { RolePicker } from "@/components/career/role-picker";
import { ResumePicker } from "@/components/resume/resume-picker";
import { apiPost } from "@/lib/api-client";
import { useSession } from "@/context/session-context";
import type { CareerPathsResponse } from "@/types/career";
import type { ResumeListItem } from "@/types/resume";

export default function TransitionsPage() {
  const { userId: sessionUserId } = useSession();
  const [selectedResumeId, setSelectedResumeId] = useState<number | null>(null);
  const [targetRoleId, setTargetRoleId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<CareerPathsResponse | null>(null);

  const handleResumeSelect = (resume: ResumeListItem) => {
    setSelectedResumeId(resume.id);
  };

  const handleSearch = async () => {
    if (!sessionUserId || !targetRoleId || !selectedResumeId) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiPost<CareerPathsResponse>(
        "/career/transition-paths",
        {
          user_id: sessionUserId,
          target_role_id: targetRoleId,
          resume_id: selectedResumeId,
        },
      );
      setResults(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Pathfinding failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Career GPS</h2>
        <p className="text-muted-foreground">
          Find multi-step career transition paths to your target role.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Find Transition Paths
          </CardTitle>
          <CardDescription>
            Select your resume and target role to discover career paths.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <ResumePicker
              selectedResumeId={selectedResumeId}
              onSelect={handleResumeSelect}
            />
            <RolePicker
              selectedRoleId={targetRoleId}
              onSelect={setTargetRoleId}
            />
          </div>

          <Button
            onClick={handleSearch}
            disabled={isLoading || !sessionUserId || !targetRoleId || !selectedResumeId}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Finding Paths...
              </>
            ) : (
              <>
                <Navigation className="mr-2 h-4 w-4" />
                Find Career Paths
              </>
            )}
          </Button>
        </CardContent>
      </Card>

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
            {results.paths.length} path{results.paths.length !== 1 ? "s" : ""}{" "}
            to {results.target_role.title}
          </h3>
          {results.paths.map((path, i) => (
            <TransitionPathView key={i} path={path} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
