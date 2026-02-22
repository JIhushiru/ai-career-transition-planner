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
import { Input } from "@/components/ui/input";
import { TransitionPathView } from "@/components/career/transition-path";
import { RolePicker } from "@/components/career/role-picker";
import { apiPost } from "@/lib/api-client";
import { useSession } from "@/context/session-context";
import type { CareerPathsResponse } from "@/types/career";

export default function TransitionsPage() {
  const { userId: sessionUserId } = useSession();
  const [targetRoleId, setTargetRoleId] = useState<number | null>(null);
  const [maxSteps, setMaxSteps] = useState("3");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<CareerPathsResponse | null>(null);

  const handleSearch = async () => {
    if (!sessionUserId || !targetRoleId) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiPost<CareerPathsResponse>(
        "/career/transition-paths",
        {
          user_id: sessionUserId,
          target_role_id: targetRoleId,
          max_steps: parseInt(maxSteps) || 3,
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
            Run career matching first, then select a target role.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <RolePicker
              selectedRoleId={targetRoleId}
              onSelect={setTargetRoleId}
            />
            <div>
              <label className="mb-1 block text-sm font-medium">
                Max Steps
              </label>
              <Input
                type="number"
                min="1"
                max="5"
                value={maxSteps}
                onChange={(e) => setMaxSteps(e.target.value)}
              />
            </div>
          </div>

          <Button
            onClick={handleSearch}
            disabled={isLoading || !sessionUserId || !targetRoleId}
            className="bg-emerald-600 hover:bg-emerald-700 text-white"
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
          {results.paths.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                No transition paths found. Try a different target role or
                increase max steps.
              </CardContent>
            </Card>
          ) : (
            results.paths.map((path, i) => (
              <TransitionPathView key={i} path={path} index={i} />
            ))
          )}
        </div>
      )}
    </div>
  );
}
