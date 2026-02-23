"use client";

import { useState } from "react";
import { Loader2, Users, Lightbulb, ArrowRight, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { RolePicker } from "@/components/career/role-picker";
import { apiGet } from "@/lib/api-client";
import { useSession } from "@/context/session-context";
import type { SuccessStoriesResponse, SuccessStory } from "@/types/career";

function StoryCard({ story }: { story: SuccessStory }) {
  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardContent className="pt-6 space-y-3">
        <div className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-violet-100 text-sm font-bold text-violet-700 dark:bg-violet-900 dark:text-violet-300">
            {story.name[0]}
          </span>
          <div>
            <p className="text-sm font-medium">{story.name}</p>
            <p className="text-xs text-muted-foreground">
              {story.from_role}{" "}
              <ArrowRight className="inline h-3 w-3 mx-0.5" />
              {story.to_role}
            </p>
          </div>
        </div>

        <p className="text-sm leading-relaxed text-foreground/90">
          {story.story}
        </p>

        <div className="flex items-start gap-2 rounded-md bg-amber-50 dark:bg-amber-950/20 p-3">
          <Lightbulb className="h-4 w-4 mt-0.5 text-amber-600 dark:text-amber-400 shrink-0" />
          <p className="text-xs text-amber-800 dark:text-amber-300">
            {story.tip}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

export default function StoriesPage() {
  const { userId } = useSession();
  const [targetRoleId, setTargetRoleId] = useState<number | null>(null);
  const [stories, setStories] = useState<SuccessStory[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLoad = async () => {
    if (!userId || !targetRoleId) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiGet<SuccessStoriesResponse>(
        `/career/stories/${userId}?target_role_id=${targetRoleId}&count=3`
      );
      setStories(res.stories);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load stories"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Users className="h-6 w-6 text-violet-600" />
          People Like You
        </h2>
        <p className="text-muted-foreground">
          See how others with similar backgrounds made successful career
          transitions.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Choose Your Target Role
          </CardTitle>
          <CardDescription>
            Select the role you&apos;re interested in to see relevant success stories.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <RolePicker
            selectedRoleId={targetRoleId}
            onSelect={setTargetRoleId}
          />
          <div className="flex gap-2">
            <Button
              onClick={handleLoad}
              disabled={isLoading || !userId || !targetRoleId}
              className="bg-violet-600 hover:bg-violet-700 text-white"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Loading...
                </>
              ) : (
                <>
                  <Users className="mr-2 h-4 w-4" />
                  Show Stories
                </>
              )}
            </Button>
            {stories.length > 0 && (
              <Button
                variant="outline"
                onClick={handleLoad}
                disabled={isLoading}
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                New Stories
              </Button>
            )}
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

      {stories.length > 0 && (
        <div className="space-y-4">
          {stories.map((story, i) => (
            <StoryCard key={`${story.name}-${i}`} story={story} />
          ))}
          <p className="text-center text-xs text-muted-foreground">
            These stories are generated templates based on real career transition
            patterns in the Philippine job market.
          </p>
        </div>
      )}
    </div>
  );
}
