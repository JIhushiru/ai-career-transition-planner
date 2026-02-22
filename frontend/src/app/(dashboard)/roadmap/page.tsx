"use client";

import { useState, useEffect } from "react";
import { Loader2, Map } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { RoadmapView } from "@/components/career/roadmap-view";
import { apiPost } from "@/lib/api-client";
import { useSession } from "@/context/session-context";
import type { RoadmapResponse } from "@/types/career";

export default function RoadmapPage() {
  const { userId: sessionUserId } = useSession();
  const [userId, setUserId] = useState("");
  const [targetRoleId, setTargetRoleId] = useState("");

  useEffect(() => {
    if (sessionUserId && !userId) {
      setUserId(String(sessionUserId));
    }
  }, [sessionUserId]);
  const [includeResources, setIncludeResources] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null);

  const handleGenerate = async () => {
    if (!userId.trim() || !targetRoleId.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiPost<RoadmapResponse>("/career/roadmap", {
        user_id: parseInt(userId),
        target_role_id: parseInt(targetRoleId),
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
            <div>
              <label className="mb-1 block text-xs font-medium">User ID</label>
              <Input
                placeholder="e.g., 1"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium">
                Target Role ID
              </label>
              <Input
                placeholder="e.g., 15"
                value={targetRoleId}
                onChange={(e) => setTargetRoleId(e.target.value)}
              />
            </div>
          </div>

          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={includeResources}
              onChange={(e) => setIncludeResources(e.target.checked)}
              className="rounded"
            />
            Include learning resources (uses Gemini search, requires API key)
          </label>

          <Button
            onClick={handleGenerate}
            disabled={isLoading || !userId.trim() || !targetRoleId.trim()}
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
          <CardContent className="py-4 text-sm text-destructive">
            {error}
          </CardContent>
        </Card>
      )}

      {roadmap && <RoadmapView roadmap={roadmap} />}
    </div>
  );
}
