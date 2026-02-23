"use client";

import { useState, useRef, useCallback } from "react";
import {
  Loader2,
  Star,
  Target,
  Calendar,
  Briefcase,
  GraduationCap,
  MessageSquare,
  FolderOpen,
  ChevronDown,
  ChevronUp,
  Clock,
  TrendingUp,
  CheckCircle2,
  AlertCircle,
  Download,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { RolePicker } from "@/components/career/role-picker";
import { ResumePicker } from "@/components/resume/resume-picker";
import { apiPost } from "@/lib/api-client";
import { safeParseInt } from "@/lib/constants";
import { useSession } from "@/context/session-context";
import type { DreamJobPlanResponse } from "@/types/career";
import type { ResumeListItem } from "@/types/resume";

export default function DreamJobPage() {
  const { userId: sessionUserId, currentSalary } = useSession();
  const [selectedResumeId, setSelectedResumeId] = useState<number | null>(null);
  const [dreamRoleId, setDreamRoleId] = useState<number | null>(null);
  const [yearsExp, setYearsExp] = useState<string>("");
  const [salary, setSalary] = useState<string>(currentSalary?.toString() || "");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [plan, setPlan] = useState<DreamJobPlanResponse | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(["paths", "skills", "weekly", "interview", "portfolio"])
  );

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(section)) next.delete(section);
      else next.add(section);
      return next;
    });
  };

  const handleResumeSelect = (resume: ResumeListItem) => {
    setSelectedResumeId(resume.id);
  };

  const handleGenerate = async () => {
    if (!sessionUserId || !dreamRoleId || !selectedResumeId) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiPost<DreamJobPlanResponse>("/career/dream-job", {
        user_id: sessionUserId,
        dream_role_id: dreamRoleId,
        resume_id: selectedResumeId,
        years_experience: safeParseInt(yearsExp) ?? undefined,
        current_salary: safeParseInt(salary) ?? undefined,
      });
      setPlan(res);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate plan"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const planRef = useRef<HTMLDivElement>(null);

  const handleExportPDF = useCallback(() => {
    // Expand all sections before printing
    setExpandedSections(new Set(["paths", "skills", "weekly", "interview", "portfolio"]));
    // Give React a tick to re-render expanded sections
    setTimeout(() => {
      window.print();
    }, 100);
  }, []);

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Star className="h-6 w-6 text-amber-500" />
          Dream Job Planner
        </h2>
        <p className="text-muted-foreground">
          Tell us your dream job and we&apos;ll reverse-engineer a complete plan
          to get you there.
        </p>
      </div>

      {/* Input Form */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            What&apos;s your dream job?
          </CardTitle>
          <CardDescription>
            Select your target role and we&apos;ll build your personalized
            career plan.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <ResumePicker
              selectedResumeId={selectedResumeId}
              onSelect={handleResumeSelect}
            />
            <RolePicker
              selectedRoleId={dreamRoleId}
              onSelect={setDreamRoleId}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="dream-years-exp" className="text-sm font-medium">
                Years of Experience
              </label>
              <input
                id="dream-years-exp"
                type="number"
                min="0"
                max="30"
                value={yearsExp}
                onChange={(e) => setYearsExp(e.target.value)}
                placeholder="e.g. 3"
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label htmlFor="dream-salary" className="text-sm font-medium">
                Current Salary (PHP/mo)
              </label>
              <input
                id="dream-salary"
                type="number"
                min="0"
                value={salary}
                onChange={(e) => setSalary(e.target.value)}
                placeholder="e.g. 40000"
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
              />
            </div>
          </div>

          <Button
            onClick={handleGenerate}
            disabled={isLoading || !sessionUserId || !dreamRoleId || !selectedResumeId}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Building your plan...
              </>
            ) : (
              <>
                <Star className="mr-2 h-4 w-4" />
                Build My Dream Plan
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

      {plan && (
        <div ref={planRef} className="space-y-6 print:space-y-4">
          {/* Export Button */}
          <div className="flex justify-end no-print">
            <Button
              variant="outline"
              size="sm"
              onClick={handleExportPDF}
            >
              <Download className="mr-2 h-4 w-4" />
              Export as PDF
            </Button>
          </div>

          {/* Dream Role Summary */}
          <Card className="border-amber-200 bg-amber-50/50 dark:border-amber-800 dark:bg-amber-950/20">
            <CardContent className="py-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-bold">{plan.dream_role.title}</h3>
                  <p className="text-sm text-muted-foreground">
                    {plan.dream_role.category} &middot;{" "}
                    {plan.dream_role.seniority} level
                  </p>
                  <p className="mt-1 text-sm">{plan.dream_role.description}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">
                    {plan.dream_role.salary_range_ph}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {plan.dream_role.salary_range_usd}
                  </p>
                </div>
              </div>
              <div className="mt-3 flex items-center gap-4">
                <div className="flex items-center gap-1 text-sm">
                  <TrendingUp className="h-4 w-4 text-green-600" />
                  <span>
                    {plan.skill_analysis.match_percentage}% skill match
                  </span>
                </div>
                <div className="flex items-center gap-1 text-sm">
                  <Clock className="h-4 w-4 text-blue-600" />
                  <span>
                    ~{plan.skill_analysis.total_learning_hours}h to learn
                  </span>
                </div>
                {plan.career_paths.length > 0 && (
                  <div className="flex items-center gap-1 text-sm">
                    <Target className="h-4 w-4 text-purple-600" />
                    <span>
                      ~{plan.career_paths[0].total_months} months via best path
                    </span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Career Paths */}
          {plan.career_paths.length > 0 && (
            <CollapsibleSection
              title="Career Path"
              icon={<Target className="h-5 w-5 text-purple-600" />}
              subtitle={`${plan.career_paths.length} path(s) found`}
              isExpanded={expandedSections.has("paths")}
              onToggle={() => toggleSection("paths")}
            >
              <div className="space-y-4">
                {plan.career_paths.map((path, pathIdx) => (
                  <div key={pathIdx} className="space-y-2">
                    <div className="flex items-center gap-2 text-sm font-medium">
                      <span className="rounded bg-purple-100 px-2 py-0.5 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">
                        Path {pathIdx + 1}
                      </span>
                      <span className="text-muted-foreground">
                        {path.total_months} months &middot; Difficulty:{" "}
                        {Math.round(path.total_difficulty * 100)}%
                      </span>
                    </div>
                    <div className="flex flex-wrap items-center gap-1">
                      {path.steps.map((step, stepIdx) => (
                        <div key={stepIdx} className="flex items-center gap-1">
                          {stepIdx === 0 && (
                            <span className="rounded border px-2 py-1 text-xs font-medium">
                              {step.from_role}
                            </span>
                          )}
                          <span className="text-xs text-muted-foreground">
                            &rarr;{" "}
                            <span className="text-[10px]">
                              {step.months}mo
                            </span>
                          </span>
                          <span className="rounded border px-2 py-1 text-xs font-medium">
                            {step.to_role}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CollapsibleSection>
          )}

          {/* Skill Analysis */}
          <CollapsibleSection
            title="Skill Gap Analysis"
            icon={<GraduationCap className="h-5 w-5 text-blue-600" />}
            subtitle={`${plan.skill_analysis.skills_to_learn.length} skills to learn`}
            isExpanded={expandedSections.has("skills")}
            onToggle={() => toggleSection("skills")}
          >
            <div className="space-y-3">
              {plan.skill_analysis.skills_matched.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-green-700 dark:text-green-400 mb-1">
                    Skills You Already Have
                  </h4>
                  <div className="flex flex-wrap gap-1">
                    {plan.skill_analysis.skills_matched.map((s) => (
                      <span
                        key={s}
                        className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      >
                        <CheckCircle2 className="h-3 w-3" />
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <div>
                <h4 className="text-sm font-medium text-orange-700 dark:text-orange-400 mb-1">
                  Skills to Learn
                </h4>
                <div className="space-y-1">
                  {plan.skill_analysis.skills_to_learn.map((g) => (
                    <div
                      key={g.skill}
                      className="flex items-center justify-between rounded border px-3 py-1.5 text-sm"
                    >
                      <div className="flex items-center gap-2">
                        <AlertCircle
                          className={`h-3.5 w-3.5 ${
                            g.priority === "high"
                              ? "text-red-500"
                              : "text-yellow-500"
                          }`}
                        />
                        <span>{g.skill}</span>
                      </div>
                      <span className="text-xs text-muted-foreground">
                        ~{g.estimated_hours}h
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CollapsibleSection>

          {/* Weekly Action Plan */}
          {plan.weekly_plan.length > 0 && (
            <CollapsibleSection
              title="Weekly Action Plan"
              icon={<Calendar className="h-5 w-5 text-green-600" />}
              subtitle={`${plan.weekly_plan.at(-1)?.week_end || plan.weekly_plan.at(-1)?.week || plan.weekly_plan.length} weeks`}
              isExpanded={expandedSections.has("weekly")}
              onToggle={() => toggleSection("weekly")}
            >
              <div className="space-y-2">
                {plan.weekly_plan.map((week) => (
                  <div
                    key={week.week}
                    className="rounded border p-3 text-sm"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">
                        {week.week_label || `Week ${week.week}`}{" "}
                        <span className="text-muted-foreground font-normal">
                          &middot; {week.phase}
                        </span>
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {week.start_date} &middot; {week.hours}h
                        {week.hours_per_week && week.hours > week.hours_per_week && (
                          <> ({week.hours_per_week}h/wk)</>
                        )}
                      </span>
                    </div>
                    {week.focus_skills.length > 0 && (
                      <div className="mt-1 flex flex-wrap gap-1">
                        {week.focus_skills.map((s) => (
                          <span
                            key={s}
                            className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    )}
                    <ul className="mt-2 space-y-1 text-xs text-muted-foreground">
                      {week.actions.map((a, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <span className="mt-0.5 h-1 w-1 rounded-full bg-muted-foreground shrink-0" />
                          {a}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </CollapsibleSection>
          )}

          {/* Interview Prep */}
          <CollapsibleSection
            title="Interview Preparation"
            icon={<MessageSquare className="h-5 w-5 text-indigo-600" />}
            subtitle="Questions, topics & tips"
            isExpanded={expandedSections.has("interview")}
            onToggle={() => toggleSection("interview")}
          >
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium mb-2">
                  Behavioral Questions to Practice
                </h4>
                <ul className="space-y-1.5">
                  {plan.interview_prep.behavioral_questions.map((q, i) => (
                    <li key={i} className="text-sm text-muted-foreground">
                      {i + 1}. {q}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="text-sm font-medium mb-2">
                  Technical Topics
                </h4>
                <div className="space-y-1">
                  {plan.interview_prep.technical_topics.map((t) => (
                    <div
                      key={t.skill}
                      className="flex items-center justify-between rounded border px-3 py-1.5 text-sm"
                    >
                      <div className="flex items-center gap-2">
                        {t.strength === "strong" ? (
                          <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
                        ) : (
                          <AlertCircle className="h-3.5 w-3.5 text-orange-500" />
                        )}
                        <span>{t.skill}</span>
                      </div>
                      <span className="text-xs text-muted-foreground max-w-xs truncate">
                        {t.prep_tip}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {plan.interview_prep.role_specific_areas.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium mb-2">
                    Role-Specific Areas
                  </h4>
                  <ul className="space-y-1">
                    {plan.interview_prep.role_specific_areas.map((a, i) => (
                      <li
                        key={i}
                        className="text-sm text-muted-foreground flex items-start gap-1.5"
                      >
                        <Briefcase className="h-3.5 w-3.5 mt-0.5 shrink-0" />
                        {a}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div>
                <h4 className="text-sm font-medium mb-2">
                  Preparation Tips
                </h4>
                <ul className="space-y-1">
                  {plan.interview_prep.preparation_tips.map((tip, i) => (
                    <li
                      key={i}
                      className="text-sm text-muted-foreground flex items-start gap-1.5"
                    >
                      <CheckCircle2 className="h-3.5 w-3.5 mt-0.5 text-green-500 shrink-0" />
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </CollapsibleSection>

          {/* Portfolio Projects */}
          <CollapsibleSection
            title="Portfolio Projects"
            icon={<FolderOpen className="h-5 w-5 text-teal-600" />}
            subtitle={`${plan.portfolio_projects.length} suggested projects`}
            isExpanded={expandedSections.has("portfolio")}
            onToggle={() => toggleSection("portfolio")}
          >
            <div className="space-y-3">
              {plan.portfolio_projects.map((project, i) => (
                <div key={i} className="rounded border p-4">
                  <div className="flex items-start justify-between">
                    <h4 className="font-medium text-sm">{project.title}</h4>
                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded px-1.5 py-0.5 text-xs ${
                          project.complexity === "high"
                            ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                            : project.complexity === "medium"
                            ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
                            : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                        }`}
                      >
                        {project.complexity}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        ~{project.estimated_hours}h
                      </span>
                    </div>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {project.description}
                  </p>
                  {project.skills_demonstrated.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {project.skills_demonstrated.map((s) => (
                        <span
                          key={s}
                          className="rounded bg-teal-100 px-1.5 py-0.5 text-[10px] text-teal-700 dark:bg-teal-900/30 dark:text-teal-400"
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CollapsibleSection>
        </div>
      )}
    </div>
  );
}

function CollapsibleSection({
  title,
  icon,
  subtitle,
  isExpanded,
  onToggle,
  children,
}: {
  title: string;
  icon: React.ReactNode;
  subtitle: string;
  isExpanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}) {
  return (
    <Card>
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between px-6 py-4 text-left"
      >
        <div className="flex items-center gap-3">
          {icon}
          <div>
            <h3 className="font-medium">{title}</h3>
            <p className="text-xs text-muted-foreground">{subtitle}</p>
          </div>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        )}
      </button>
      {isExpanded && <CardContent className="pt-0">{children}</CardContent>}
    </Card>
  );
}
