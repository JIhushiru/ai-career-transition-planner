"use client";

import { useState, useEffect } from "react";
import { Loader2 } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { SkillList } from "@/components/resume/skill-list";
import { ResumePicker } from "@/components/resume/resume-picker";
import { apiGet } from "@/lib/api-client";
import type { SkillsResponse } from "@/types/resume";
import type { ResumeListItem } from "@/types/resume";

export default function SkillsPage() {
  const [selectedResumeId, setSelectedResumeId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<SkillsResponse | null>(null);

  const fetchSkills = async (resumeId: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await apiGet<SkillsResponse>(
        `/resume/${resumeId}/skills`,
      );
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch skills");
    } finally {
      setIsLoading(false);
    }
  };

  const handleResumeSelect = (resume: ResumeListItem) => {
    setSelectedResumeId(resume.id);
  };

  useEffect(() => {
    if (selectedResumeId) {
      fetchSkills(selectedResumeId);
    }
  }, [selectedResumeId]);

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Extracted Skills</h2>
        <p className="text-muted-foreground">
          View and manage skills extracted from your resume.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Select Resume
          </CardTitle>
          <CardDescription>
            Choose a resume to view its extracted skills.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <ResumePicker
            selectedResumeId={selectedResumeId}
            onSelect={handleResumeSelect}
          />
          {isLoading && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading skills...
            </div>
          )}
        </CardContent>
      </Card>

      {error && (
        <Card className="border-destructive">
          <CardContent className="py-4 text-sm text-destructive">
            {error}
          </CardContent>
        </Card>
      )}

      {data && <SkillList skills={data.skills} />}
    </div>
  );
}
