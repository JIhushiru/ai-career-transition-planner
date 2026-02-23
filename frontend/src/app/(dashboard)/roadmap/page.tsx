"use client";

import { useState } from "react";
import { Loader2, Map } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { RoadmapView } from "@/components/career/roadmap-view";
import { RolePicker } from "@/components/career/role-picker";
import { ResumePicker } from "@/components/resume/resume-picker";
import { apiPost } from "@/lib/api-client";
import { useSession } from "@/context/session-context";
import type { RoadmapResponse } from "@/types/career";
import type { ResumeListItem } from "@/types/resume";

export default function RoadmapPage() {
  const { userId: sessionUserId } = useSession();
  const [selectedResumeId, setSelectedResumeId] = useState<number | null>(null);
  const [targetRoleId, setTargetRoleId] = useState<number | null>(null);
  const [includeResources, setIncludeResources] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null);

  const handleResumeSelect = (resume: ResumeListItem) => {
    setSelectedResumeId(resume.id);
  };

  const handleGenerate = async () => {
    if (!sessionUserId || !targetRoleId || !selectedResumeId) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiPost<RoadmapResponse>("/career/roadmap", {
        user_id: sessionUserId,
        target_role_id: targetRoleId,
        resume_id: selectedResumeId,
        include_resources: includeResources,
      });
      setRoadmap(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Roadmap generation failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Learning Roadmap</h2>
        <p className="text-muted-foreground">
          Personalized skill gap analysis with learning recommendations.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Generate Roadmap
          </CardTitle>
          <CardDescription>
            Get a learning plan to bridge skill gaps for your target role.
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

          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={includeResources}
              onChange={(e) => setIncludeResources(e.target.checked)}
              className="h-4 w-4 rounded border-input accent-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
            Include learning resources
          </label>

          <Button
            onClick={handleGenerate}
            disabled={isLoading || !sessionUserId || !targetRoleId || !selectedResumeId}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Map className="mr-2 h-4 w-4" />
                Generate Roadmap
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

      {roadmap && <RoadmapView roadmap={roadmap} />}
    </div>
  );
}
