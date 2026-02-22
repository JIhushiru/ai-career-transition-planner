"use client";

import { useState } from "react";
import Link from "next/link";
import { Compass } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { UploadForm } from "@/components/resume/upload-form";
import { TextPasteForm } from "@/components/resume/text-paste-form";
import { SkillList } from "@/components/resume/skill-list";
import { apiUpload, apiPost } from "@/lib/api-client";
import { useSession } from "@/context/session-context";
import type { ResumeUploadResponse, ExtractedSkill } from "@/types/resume";

export default function ResumePage() {
  const { setSession } = useSession();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [skills, setSkills] = useState<ExtractedSkill[]>([]);
  const [resumeId, setResumeId] = useState<number | null>(null);
  const [rawText, setRawText] = useState<string>("");

  const handleResult = (result: ResumeUploadResponse) => {
    setSkills(result.skills);
    setResumeId(result.resume_id);
    setRawText(result.raw_text);
    setSession(result.user_id, result.resume_id);
  };

  const handleUpload = async (file: File) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await apiUpload<ResumeUploadResponse>(
        "/resume/upload",
        file,
      );
      handleResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextSubmit = async (text: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await apiPost<ResumeUploadResponse>(
        "/resume/parse-text",
        { text },
      );
      handleResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Parsing failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Resume Parser</h2>
        <p className="text-muted-foreground">
          Upload your resume or paste text to extract skills and experience.
        </p>
      </div>

      <Tabs defaultValue="upload">
        <TabsList>
          <TabsTrigger value="upload">Upload PDF</TabsTrigger>
          <TabsTrigger value="paste">Paste Text</TabsTrigger>
        </TabsList>
        <TabsContent value="upload" className="mt-4">
          <UploadForm onUpload={handleUpload} isLoading={isLoading} />
        </TabsContent>
        <TabsContent value="paste" className="mt-4">
          <TextPasteForm onSubmit={handleTextSubmit} isLoading={isLoading} />
        </TabsContent>
      </Tabs>

      {error && (
        <Card className="border-destructive">
          <CardContent className="py-4 text-sm text-destructive">
            {error}
          </CardContent>
        </Card>
      )}

      {skills.length > 0 && (
        <>
          <SkillList skills={skills} />

          <Card className="border-primary/20 bg-primary/5">
            <CardContent className="flex items-center justify-between py-4">
              <p className="text-sm font-medium">
                {skills.length} skills extracted — ready to find matching
                careers!
              </p>
              <Button asChild>
                <Link href="/explore">
                  <Compass className="mr-2 h-4 w-4" />
                  Explore Careers
                </Link>
              </Button>
            </CardContent>
          </Card>

          {rawText && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">
                  Extracted Text
                </CardTitle>
                <CardDescription>
                  Resume ID: {resumeId} &middot; {rawText.length} characters
                </CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="max-h-64 overflow-y-auto whitespace-pre-wrap rounded bg-muted p-4 font-mono text-xs">
                  {rawText}
                </pre>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
