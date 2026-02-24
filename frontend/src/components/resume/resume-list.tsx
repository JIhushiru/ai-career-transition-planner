"use client";

import { useState, useEffect } from "react";
import { Download, FileText, ClipboardPaste, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { apiGet } from "@/lib/api-client";
import { STORAGE_KEYS } from "@/lib/constants";
import type { ResumeListItem, ResumeListResponse } from "@/types/resume";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function handleDownload(resume: ResumeListItem) {
  const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
  const url = `${API_BASE}/resume/${resume.id}/download`;

  const a = document.createElement("a");
  // Use fetch to include auth header, then trigger download
  fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
    .then((res) => {
      if (!res.ok) throw new Error("Download failed");
      return res.blob();
    })
    .then((blob) => {
      const blobUrl = URL.createObjectURL(blob);
      a.href = blobUrl;
      a.download =
        resume.filename?.replace(/\.pdf$/i, ".txt") ??
        `resume_${resume.id}.txt`;
      a.click();
      URL.revokeObjectURL(blobUrl);
    });
}

export function ResumeList() {
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiGet<ResumeListResponse>("/resume/list");
        setResumes(data.resumes);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load resumes",
        );
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          <span className="ml-2 text-sm text-muted-foreground">
            Loading resumes...
          </span>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-destructive">
        <CardContent role="alert" className="py-4 text-sm text-destructive">
          {error}
        </CardContent>
      </Card>
    );
  }

  if (resumes.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-muted-foreground">
          No resumes uploaded yet. Use the tabs above to upload a PDF or paste
          text.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">My Resumes</CardTitle>
        <CardDescription>
          {resumes.length} resume{resumes.length !== 1 ? "s" : ""} uploaded
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        {resumes.map((resume) => (
          <div
            key={resume.id}
            className="flex items-center justify-between gap-4 rounded-lg border p-3 transition-colors hover:bg-muted/50"
          >
            <div className="flex items-center gap-3 min-w-0">
              {resume.source_type === "pdf" ? (
                <FileText className="h-5 w-5 shrink-0 text-red-500" />
              ) : (
                <ClipboardPaste className="h-5 w-5 shrink-0 text-blue-500" />
              )}
              <div className="min-w-0">
                <p className="truncate text-sm font-medium">
                  {resume.filename || "Text paste"}
                </p>
                <p className="text-xs text-muted-foreground">
                  {formatDate(resume.created_at)}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <Badge variant="secondary" className="text-xs">
                {resume.skill_count} skill{resume.skill_count !== 1 ? "s" : ""}
              </Badge>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => handleDownload(resume)}
                title="Download extracted text"
              >
                <Download className="h-4 w-4" />
                <span className="sr-only">Download</span>
              </Button>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
