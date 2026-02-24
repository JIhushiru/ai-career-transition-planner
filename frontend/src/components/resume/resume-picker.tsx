"use client";

import { useState, useEffect } from "react";
import { AlertCircle, FileText, ChevronDown } from "lucide-react";
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
    return (
      <div className="space-y-2">
        <label className="block text-xs font-medium text-muted-foreground uppercase tracking-wide">
          Resume
        </label>
        <div className="h-10 animate-pulse rounded-lg bg-muted" />
      </div>
    );
  }

  if (error) {
    return <p role="alert" className="text-sm text-destructive">{error}</p>;
  }

  if (resumes.length === 0) {
    return (
      <div className="flex items-center gap-3 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 dark:border-amber-800 dark:bg-amber-900/30">
        <AlertCircle className="h-5 w-5 shrink-0 text-amber-600 dark:text-amber-300" />
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
    <div className="space-y-2">
      <label className="block text-xs font-medium text-muted-foreground uppercase tracking-wide">
        Resume
      </label>
      <div className="relative">
        <FileText className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <select
          aria-label="Select resume"
          className="h-10 w-full appearance-none rounded-lg border bg-background pl-9 pr-9 text-sm font-medium transition-colors hover:border-foreground/25 focus:border-ring focus:outline-none focus:ring-2 focus:ring-ring/20"
          value={selectedResumeId ?? ""}
          onChange={(e) => {
            const r = resumes.find((r) => r.id === parseInt(e.target.value, 10));
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
        <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      </div>
    </div>
  );
}
