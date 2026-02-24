"use client";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { ExtractedSkill } from "@/types/resume";

const categoryColors: Record<string, string> = {
  technical: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
  framework: "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300",
  tool: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
  soft: "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300",
  domain: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-300",
  certification: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300",
  other: "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300",
};

const categoryLabels: Record<string, string> = {
  technical: "Programming Languages",
  framework: "Frameworks & Libraries",
  tool: "Tools & Platforms",
  soft: "Soft Skills",
  domain: "Domain Knowledge",
  certification: "Certifications",
  other: "Other",
};

interface SkillListProps {
  skills: ExtractedSkill[];
}

export function SkillList({ skills }: SkillListProps) {
  const grouped = skills.reduce<Record<string, ExtractedSkill[]>>(
    (acc, skill) => {
      const cat = skill.category || "other";
      if (!acc[cat]) acc[cat] = [];
      acc[cat].push(skill);
      return acc;
    },
    {},
  );

  const sortedCategories = Object.entries(grouped).sort(
    ([, a], [, b]) => b.length - a.length,
  );

  if (skills.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-muted-foreground">
          No skills extracted yet. Upload a resume to get started.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {skills.length} skills extracted
        </p>
      </div>

      {sortedCategories.map(([category, categorySkills]) => (
        <Card key={category}>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">
              {categoryLabels[category] || category}
            </CardTitle>
            <CardDescription>
              {categorySkills.length} skill
              {categorySkills.length !== 1 ? "s" : ""}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {categorySkills.map((skill) => (
                <Badge
                  key={skill.name}
                  variant="secondary"
                  className={categoryColors[category] || categoryColors.other}
                >
                  {skill.name}
                  <span className="ml-1 opacity-60">
                    {Math.round(skill.confidence * 100)}%
                  </span>
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
