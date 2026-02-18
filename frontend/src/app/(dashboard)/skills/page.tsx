"use client";

import { useState } from "react";
import { Search, Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { SkillList } from "@/components/resume/skill-list";
import { apiGet } from "@/lib/api-client";
import type { SkillsResponse } from "@/types/resume";

export default function SkillsPage() {
  const [resumeId, setResumeId] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<SkillsResponse | null>(null);

  const handleFetch = async () => {
    if (!resumeId.trim()) return;
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
            Load Skills by Resume ID
          </CardTitle>
          <CardDescription>
            Enter the resume ID from a previous upload to view extracted skills.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Resume ID (e.g., 1)"
                value={resumeId}
                onChange={(e) => setResumeId(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleFetch()}
                className="pl-9"
              />
            </div>
            <Button onClick={handleFetch} disabled={isLoading || !resumeId.trim()}>
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                "Load"
              )}
            </Button>
          </div>
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
