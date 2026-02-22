"use client";

import { useState, useEffect } from "react";
import { AlertCircle } from "lucide-react";
import Link from "next/link";
import { apiGet } from "@/lib/api-client";
import type { ResumeListResponse, ResumeListItem } from "@/types/resume";

interface ResumePickerProps {
  selectedResumeId: number | null;
  onSelect: (resume: ResumeListItem) => void;
}

export function ResumePicker({ selectedResumeId, onSelect }: ResumePickerProps) {
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadResumes() {
      try {
        const data = await apiGet<ResumeListResponse>("/resume/list");
        setResumes(data.resumes);
        if (!selectedResumeId && data.resumes.length > 0) {
          onSelect(data.resumes[0]);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load resumes");
      } finally {
        setIsLoading(false);
      }
    }
    loadResumes();
  }, []);

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading resumes...</p>;
  }

  if (error) {
    return <p className="text-sm text-destructive">{error}</p>;
  }

  if (resumes.length === 0) {
    return (
      <div className="flex items-center gap-3 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 dark:border-amber-800 dark:bg-amber-950">
        <AlertCircle className="h-5 w-5 shrink-0 text-amber-600 dark:text-amber-400" />
        <div>
          <p className="text-sm font-medium">No resumes found</p>
          <p className="text-xs text-muted-foreground">
            <Link href="/resume" className="underline text-primary">
              Upload a resume
            </Link>{" "}
            to get started.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <label className="mb-1 block text-xs font-medium">Resume</label>
      <select
        className="w-full rounded-md border bg-background px-3 py-2 text-sm"
        value={selectedResumeId ?? ""}
        onChange={(e) => {
          const r = resumes.find((r) => r.id === parseInt(e.target.value));
          if (r) onSelect(r);
        }}
      >
        {resumes.map((r) => (
          <option key={r.id} value={r.id}>
            {r.filename || "Text paste"} ({r.skill_count} skills) -{" "}
            {new Date(r.created_at).toLocaleDateString()}
          </option>
        ))}
      </select>
    </div>
  );
}
