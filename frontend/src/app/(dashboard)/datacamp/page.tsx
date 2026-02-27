"use client";

import { useState, useMemo, useEffect } from "react";
import {
  Search,
  ExternalLink,
  BookOpen,
  Code,
  Database,
  BarChart3,
  Brain,
  Server,
  FlaskConical,
  Loader2,
  Sparkles,
  CheckCircle2,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ResumePicker } from "@/components/resume/resume-picker";
import { apiGet } from "@/lib/api-client";
import type { SkillsResponse, ExtractedSkill, ResumeListItem } from "@/types/resume";

/* ------------------------------------------------------------------ */
/*  Career track data with skill keywords for matching                */
/* ------------------------------------------------------------------ */

interface CareerTrack {
  title: string;
  description: string;
  courses: string;
  category: string;
  primaryTech: string;
  /** Skills that map to this track — used for matching against resume */
  keywords: string[];
  partner?: string;
  url: string;
}

const CAREER_TRACKS: CareerTrack[] = [
  {
    title: "Associate Data Analyst in SQL",
    description: "Gain the SQL skills you need to query a database, analyze the results, and become a SQL proficient Data Analyst. No prior coding experience required!",
    courses: "13 Courses and Projects",
    category: "Data Analysis",
    primaryTech: "SQL",
    keywords: ["sql", "postgresql", "mysql", "database", "data analysis", "excel", "spreadsheet", "reporting", "data visualization", "statistics"],
    url: "https://www.datacamp.com/tracks/associate-data-analyst-in-sql",
  },
  {
    title: "Associate Data Scientist in Python",
    description: "Learn data science in Python, from data manipulation to machine learning. This track provides the skills needed to succeed as a data scientist!",
    courses: "19 Courses and Projects",
    category: "Data Science",
    primaryTech: "Python",
    keywords: ["python", "pandas", "numpy", "scikit-learn", "matplotlib", "seaborn", "statistics", "machine learning", "data science", "data analysis", "jupyter"],
    url: "https://www.datacamp.com/tracks/associate-data-scientist-in-python",
  },
  {
    title: "Data Analyst in Power BI",
    description: "Co-created with Microsoft\u2014gain the Power BI skills you need to prepare, model, and visualize data for the PL-300 Data Analyst certification.",
    courses: "17 Courses and Projects",
    category: "Data Analysis",
    primaryTech: "Power BI",
    keywords: ["power bi", "dax", "microsoft", "data visualization", "reporting", "dashboard", "excel", "sql", "data modeling", "business intelligence", "etl"],
    partner: "Microsoft",
    url: "https://www.datacamp.com/tracks/data-analyst-in-power-bi",
  },
  {
    title: "Data Analyst in Python",
    description: "Develop your data analytics skills in Python. Gain the data analyst skills to manipulate, analyze, and visualize data. No coding experience required!",
    courses: "14 Courses and Projects",
    category: "Data Analysis",
    primaryTech: "Python",
    keywords: ["python", "pandas", "numpy", "matplotlib", "seaborn", "data analysis", "statistics", "data visualization", "jupyter", "sql"],
    url: "https://www.datacamp.com/tracks/data-analyst-in-python",
  },
  {
    title: "Associate Data Engineer in SQL",
    description: "Learn the fundamentals of data engineering: database design and data warehousing, working with technologies including PostgreSQL and Snowflake!",
    courses: "11 Courses and Projects",
    category: "Data Engineering",
    primaryTech: "SQL",
    keywords: ["sql", "postgresql", "snowflake", "database", "data warehousing", "etl", "data modeling", "data pipeline", "schema design"],
    url: "https://www.datacamp.com/tracks/associate-data-engineer-in-sql",
  },
  {
    title: "Data Engineer in Python",
    description: "Gain in-demand skills to efficiently ingest, clean, manage data, and schedule and monitor pipelines, setting you apart in the data engineering field.",
    courses: "17 Courses and Projects",
    category: "Data Engineering",
    primaryTech: "Python",
    keywords: ["python", "etl", "data pipeline", "airflow", "spark", "sql", "docker", "aws", "data warehousing", "kafka", "database"],
    url: "https://www.datacamp.com/tracks/data-engineer-in-python",
  },
  {
    title: "Associate AI Engineer for Data Scientists",
    description: "Train and fine-tune the latest AI models for production, including LLMs like Llama 3. Start your journey to becoming an AI Engineer today!",
    courses: "11 Courses and Projects",
    category: "AI & ML",
    primaryTech: "Python",
    keywords: ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "llm", "nlp", "transformers", "hugging face", "ai", "neural network", "fine-tuning"],
    url: "https://www.datacamp.com/tracks/associate-ai-engineer-for-data-scientists",
  },
  {
    title: "Associate Data Scientist in R",
    description: "Learn how to use R for data science, from data manipulation to machine learning. Gain the career-building skills you need to succeed in data science!",
    courses: "26 Courses and Projects",
    category: "Data Science",
    primaryTech: "R",
    keywords: ["r", "ggplot2", "dplyr", "tidyverse", "statistics", "machine learning", "data science", "data analysis", "data visualization"],
    url: "https://www.datacamp.com/tracks/associate-data-scientist-in-r",
  },
  {
    title: "Data Scientist in Python",
    description: "Learn data science in Python, from data manipulation to machine learning, and gain the skills needed for the Data Scientist in Python certification!",
    courses: "11 Courses and Projects",
    category: "Data Science",
    primaryTech: "Python",
    keywords: ["python", "pandas", "numpy", "scikit-learn", "machine learning", "statistics", "data science", "deep learning", "matplotlib", "sql"],
    url: "https://www.datacamp.com/tracks/data-scientist-in-python",
  },
  {
    title: "Data Analyst in Tableau",
    description: "Master Tableau for data analysis and develop your skills in one of the world's most popular BI tools. No prior experience is required.",
    courses: "9 Courses and Projects",
    category: "Data Analysis",
    primaryTech: "Tableau",
    keywords: ["tableau", "data visualization", "dashboard", "reporting", "business intelligence", "sql", "data analysis", "excel"],
    url: "https://www.datacamp.com/tracks/data-analyst-in-tableau",
  },
  {
    title: "Data Analyst in R",
    description: "From exploratory data analysis with dplyr to data visualization with ggplot2\u2014gain the career-building R skills you need to succeed as a data analyst!",
    courses: "11 Courses and Projects",
    category: "Data Analysis",
    primaryTech: "R",
    keywords: ["r", "ggplot2", "dplyr", "tidyverse", "data analysis", "data visualization", "statistics", "reporting"],
    url: "https://www.datacamp.com/tracks/data-analyst-in-r",
  },
  {
    title: "Microsoft Azure Developer Associate (AZ-204)",
    description: "Prepare for AZ-204 by building and integrating cloud applications on Microsoft Azure with hands-on, developer-focused courses.",
    courses: "7 Courses and Projects",
    category: "Cloud & DevOps",
    primaryTech: "Azure",
    keywords: ["azure", "cloud", "microsoft", "devops", "docker", "kubernetes", "ci/cd", "api", "serverless", "microservices"],
    partner: "Microsoft",
    url: "https://www.datacamp.com/tracks/microsoft-azure-developer-associate-az-204",
  },
  {
    title: "Data Scientist in R",
    description: "Learn data science with R, from data manipulation to machine learning, and gain the skills needed for the Data Scientist in R certification!",
    courses: "11 Courses and Projects",
    category: "Data Science",
    primaryTech: "R",
    keywords: ["r", "ggplot2", "dplyr", "tidyverse", "machine learning", "statistics", "data science", "data visualization"],
    url: "https://www.datacamp.com/tracks/data-scientist-in-r",
  },
  {
    title: "Associate AI Engineer for Developers",
    description: "Learn how to integrate AI into software applications using APIs and open-source libraries. Start your journey to becoming an AI Engineer today!",
    courses: "10 Courses and Projects",
    category: "AI & ML",
    primaryTech: "Python",
    keywords: ["python", "ai", "llm", "api", "openai", "langchain", "nlp", "machine learning", "transformers", "software development"],
    url: "https://www.datacamp.com/tracks/associate-ai-engineer-for-developers",
  },
  {
    title: "Associate Python Developer",
    description: "Learn Python for software development, from writing functions to defining classes. Get the necessary skills to kickstart your developer career!",
    courses: "10 Courses and Projects",
    category: "Software Dev",
    primaryTech: "Python",
    keywords: ["python", "software development", "oop", "git", "testing", "debugging", "functions", "classes"],
    url: "https://www.datacamp.com/tracks/associate-python-developer",
  },
  {
    title: "Machine Learning Scientist in Python",
    description: "Discover machine learning with Python and work towards becoming a machine learning scientist. Explore supervised, unsupervised, and deep learning.",
    courses: "24 Courses and Projects",
    category: "AI & ML",
    primaryTech: "Python",
    keywords: ["python", "machine learning", "deep learning", "scikit-learn", "tensorflow", "keras", "pytorch", "neural network", "nlp", "computer vision", "statistics"],
    url: "https://www.datacamp.com/tracks/machine-learning-scientist-in-python",
  },
  {
    title: "Machine Learning Engineer",
    description: "This career track teaches you everything you need to know about machine learning engineering and MLOps.",
    courses: "15 Courses and Projects",
    category: "AI & ML",
    primaryTech: "Python",
    keywords: ["python", "machine learning", "mlops", "docker", "aws", "deployment", "ci/cd", "data pipeline", "model monitoring", "api"],
    url: "https://www.datacamp.com/tracks/machine-learning-engineer",
  },
  {
    title: "Python Developer",
    description: "From testing code and implementing version control to web scraping and developing packages, take the next step in your Python developer journey!",
    courses: "8 Courses and Projects",
    category: "Software Dev",
    primaryTech: "Python",
    keywords: ["python", "git", "testing", "web scraping", "software development", "packaging", "oop", "api"],
    url: "https://www.datacamp.com/tracks/python-developer",
  },
  {
    title: "Data Analyst in Databricks",
    description: "Master Databricks, SQL, data visualization, and management in the Lakehouse Platform for the Databricks Data Analyst Associate certification.",
    courses: "9 Courses and Projects",
    category: "Data Analysis",
    primaryTech: "Databricks",
    keywords: ["databricks", "sql", "spark", "data visualization", "data analysis", "data lakehouse", "python", "dashboard"],
    url: "https://www.datacamp.com/tracks/data-analyst-in-databricks",
  },
  {
    title: "Professional Data Engineer in Python",
    description: "Dive deep into advanced skills and state-of-the-art tools revolutionizing data engineering roles today with our Professional Data Engineer track.",
    courses: "15 Courses and Projects",
    category: "Data Engineering",
    primaryTech: "Python",
    keywords: ["python", "spark", "airflow", "aws", "docker", "etl", "data pipeline", "kafka", "sql", "data warehousing", "ci/cd"],
    url: "https://www.datacamp.com/tracks/professional-data-engineer-in-python",
  },
  {
    title: "Associate Data Engineer in Snowflake",
    description: "Learn to design, query, and build in Snowflake - mastering Snowflake SQL for transformation and modeling to become a job-ready Data Engineer.",
    courses: "11 Courses and Projects",
    category: "Data Engineering",
    primaryTech: "Snowflake",
    keywords: ["snowflake", "sql", "data warehousing", "data modeling", "etl", "data pipeline", "cloud"],
    partner: "Snowflake",
    url: "https://www.datacamp.com/tracks/associate-data-engineer-in-snowflake",
  },
  {
    title: "SQL Server Developer",
    description: "Gain the SQL Server skills you need to write, troubleshoot, and optimize your queries using SQL Server.",
    courses: "10 Courses and Projects",
    category: "Software Dev",
    primaryTech: "SQL",
    keywords: ["sql", "sql server", "database", "t-sql", "stored procedures", "performance tuning", "data modeling"],
    url: "https://www.datacamp.com/tracks/sql-server-developer",
  },
  {
    title: "Statistician in R",
    description: "A statistician collects and analyzes data and helps companies make sense of quantitative data, including spotting trends and making predictions.",
    courses: "14 Courses and Projects",
    category: "Data Science",
    primaryTech: "R",
    keywords: ["r", "statistics", "probability", "regression", "hypothesis testing", "data analysis", "bayesian", "time series"],
    url: "https://www.datacamp.com/tracks/statistician-in-r",
  },
  {
    title: "R Developer",
    description: "Gain the career-building skills you need to succeed as an R Developer by learning to write and package code efficiently. No coding experience needed!",
    courses: "15 Courses and Projects",
    category: "Software Dev",
    primaryTech: "R",
    keywords: ["r", "software development", "packaging", "functions", "oop", "git", "testing", "shiny"],
    url: "https://www.datacamp.com/tracks/r-developer",
  },
  {
    title: "Quantitative Analyst in R",
    description: "Ensure portfolios are risk balanced, help find new trading opportunities, and evaluate asset prices using mathematical models.",
    courses: "15 Courses and Projects",
    category: "Data Science",
    primaryTech: "R",
    keywords: ["r", "finance", "quantitative analysis", "statistics", "risk management", "portfolio", "time series", "regression", "mathematics"],
    url: "https://www.datacamp.com/tracks/quantitative-analyst-in-r",
  },
  {
    title: "Machine Learning Scientist in R",
    description: "A machine learning scientist researches new approaches and builds machine learning models.",
    courses: "17 Courses and Projects",
    category: "AI & ML",
    primaryTech: "R",
    keywords: ["r", "machine learning", "statistics", "caret", "deep learning", "neural network", "regression", "classification"],
    url: "https://www.datacamp.com/tracks/machine-learning-scientist-in-r",
  },
  {
    title: "Java Developer",
    description: "Master Java development from fundamentals to testing and optimization. Build applications that are reliable and ready to ship.",
    courses: "7 Courses and Projects",
    category: "Software Dev",
    primaryTech: "Java",
    keywords: ["java", "spring", "software development", "oop", "testing", "maven", "gradle", "api"],
    url: "https://www.datacamp.com/tracks/java-developer",
  },
  {
    title: "Data Engineer in Java",
    description: "Develop essential Java skills for data engineering, from file processing and database integration to performance optimization.",
    courses: "9 Courses and Projects",
    category: "Data Engineering",
    primaryTech: "Java",
    keywords: ["java", "database", "sql", "data pipeline", "etl", "file processing", "performance", "spring"],
    url: "https://www.datacamp.com/tracks/data-engineer-in-java",
  },
];

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

const CATEGORIES = ["All", "Data Analysis", "Data Science", "Data Engineering", "AI & ML", "Software Dev", "Cloud & DevOps"] as const;

const TECH_OPTIONS = ["All", "Python", "R", "SQL", "Java", "Power BI", "Tableau", "Databricks", "Snowflake", "Azure"] as const;

const CATEGORY_STYLES: Record<string, { icon: typeof BookOpen; color: string }> = {
  "Data Analysis": {
    icon: BarChart3,
    color: "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-800",
  },
  "Data Science": {
    icon: FlaskConical,
    color: "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-900/30 dark:text-purple-300 dark:border-purple-800",
  },
  "Data Engineering": {
    icon: Database,
    color: "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-800",
  },
  "AI & ML": {
    icon: Brain,
    color: "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-900/30 dark:text-rose-300 dark:border-rose-800",
  },
  "Software Dev": {
    icon: Code,
    color: "bg-green-50 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-300 dark:border-green-800",
  },
  "Cloud & DevOps": {
    icon: Server,
    color: "bg-cyan-50 text-cyan-700 border-cyan-200 dark:bg-cyan-900/30 dark:text-cyan-300 dark:border-cyan-800",
  },
};

/* ------------------------------------------------------------------ */
/*  Matching logic                                                     */
/* ------------------------------------------------------------------ */

/** Normalise a skill name for fuzzy comparison */
function normalise(s: string): string {
  return s.toLowerCase().trim().replace(/[.\-_]/g, " ");
}

/** Compute match score (0-100) between user skills and a track's keywords */
function scoreTrack(
  userSkillSet: Set<string>,
  track: CareerTrack,
): { score: number; matched: string[] } {
  const matched: string[] = [];
  for (const kw of track.keywords) {
    const norm = normalise(kw);
    // Exact match
    if (userSkillSet.has(norm)) {
      matched.push(kw);
      continue;
    }
    // Partial: user skill contains keyword or keyword contains user skill
    for (const us of userSkillSet) {
      if (us.includes(norm) || norm.includes(us)) {
        matched.push(kw);
        break;
      }
    }
  }
  const score =
    track.keywords.length > 0
      ? Math.round((matched.length / track.keywords.length) * 100)
      : 0;
  return { score, matched };
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */

export default function DataCampPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [selectedTech, setSelectedTech] = useState<string>("All");

  // Resume / skills state
  const [selectedResumeId, setSelectedResumeId] = useState<number | null>(null);
  const [skills, setSkills] = useState<ExtractedSkill[] | null>(null);
  const [isLoadingSkills, setIsLoadingSkills] = useState(false);
  const [skillsError, setSkillsError] = useState<string | null>(null);

  // Fetch skills when resume changes
  useEffect(() => {
    if (!selectedResumeId) return;
    let cancelled = false;
    async function fetch() {
      setIsLoadingSkills(true);
      setSkillsError(null);
      try {
        const res = await apiGet<SkillsResponse>(
          `/resume/${selectedResumeId}/skills`,
        );
        if (!cancelled) setSkills(res.skills);
      } catch (err) {
        if (!cancelled)
          setSkillsError(
            err instanceof Error ? err.message : "Failed to load skills",
          );
      } finally {
        if (!cancelled) setIsLoadingSkills(false);
      }
    }
    fetch();
    return () => {
      cancelled = true;
    };
  }, [selectedResumeId]);

  const handleResumeSelect = (resume: ResumeListItem) => {
    setSelectedResumeId(resume.id);
  };

  // Build normalised skill set from resume
  const userSkillSet = useMemo(() => {
    if (!skills) return null;
    const set = new Set<string>();
    for (const s of skills) {
      set.add(normalise(s.name));
    }
    return set;
  }, [skills]);

  // Score + filter + sort tracks
  const scoredTracks = useMemo(() => {
    return CAREER_TRACKS.map((track) => {
      const result = userSkillSet
        ? scoreTrack(userSkillSet, track)
        : { score: 0, matched: [] as string[] };
      return { ...track, ...result };
    });
  }, [userSkillSet]);

  const filteredTracks = useMemo(() => {
    const filtered = scoredTracks.filter((track) => {
      const matchesSearch =
        searchQuery === "" ||
        track.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        track.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory =
        selectedCategory === "All" || track.category === selectedCategory;
      const matchesTech =
        selectedTech === "All" || track.primaryTech === selectedTech;
      return matchesSearch && matchesCategory && matchesTech;
    });
    // Sort by score descending when skills are loaded
    if (userSkillSet) {
      filtered.sort((a, b) => b.score - a.score);
    }
    return filtered;
  }, [scoredTracks, searchQuery, selectedCategory, selectedTech, userSkillSet]);

  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = { All: CAREER_TRACKS.length };
    for (const track of CAREER_TRACKS) {
      counts[track.category] = (counts[track.category] || 0) + 1;
    }
    return counts;
  }, []);

  const hasSkills = skills !== null && skills.length > 0;

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">
          DataCamp Career Tracks
        </h2>
        <p className="text-muted-foreground">
          Select your resume to see which of the {CAREER_TRACKS.length} career
          tracks align with your skills, ranked by match.
        </p>
      </div>

      {/* Resume picker */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Match Against Your Skills
          </CardTitle>
          <CardDescription>
            Choose a resume so we can score each track based on your existing
            skills.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <ResumePicker
            selectedResumeId={selectedResumeId}
            onSelect={handleResumeSelect}
          />
          {isLoadingSkills && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Analyzing your skills...
            </div>
          )}
          {skillsError && (
            <p className="text-sm text-destructive">{skillsError}</p>
          )}
          {hasSkills && (
            <div className="rounded-lg border bg-muted/50 p-3">
              <p className="mb-2 text-xs font-medium text-muted-foreground uppercase tracking-wide">
                Your Skills ({skills.length})
              </p>
              <div className="flex flex-wrap gap-1.5">
                {skills.map((s) => (
                  <Badge key={s.name} variant="secondary" className="text-xs">
                    {s.name}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Filter Tracks
          </CardTitle>
          <CardDescription>
            Narrow down by category, technology, or keyword.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search career tracks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">Category</label>
            <div className="flex flex-wrap gap-2">
              {CATEGORIES.map((cat) => (
                <Badge
                  key={cat}
                  variant={selectedCategory === cat ? "default" : "outline"}
                  className="cursor-pointer px-3 py-1"
                  onClick={() => setSelectedCategory(cat)}
                >
                  {cat}
                  {categoryCounts[cat] !== undefined && (
                    <span className="ml-1 opacity-70">
                      ({categoryCounts[cat]})
                    </span>
                  )}
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">
              Technology
            </label>
            <div className="flex flex-wrap gap-2">
              {TECH_OPTIONS.map((tech) => (
                <Badge
                  key={tech}
                  variant={selectedTech === tech ? "default" : "outline"}
                  className="cursor-pointer px-3 py-1"
                  onClick={() => setSelectedTech(tech)}
                >
                  {tech}
                </Badge>
              ))}
            </div>
          </div>

          {(searchQuery || selectedCategory !== "All" || selectedTech !== "All") && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setSearchQuery("");
                setSelectedCategory("All");
                setSelectedTech("All");
              }}
            >
              Clear filters
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Results count */}
      <p className="text-sm text-muted-foreground">
        Showing {filteredTracks.length} of {CAREER_TRACKS.length} tracks
        {hasSkills && " \u2014 sorted by skill match"}
      </p>

      {/* Track cards */}
      {filteredTracks.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            No tracks match your filters. Try broadening your search.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {filteredTracks.map((track) => {
            const style = CATEGORY_STYLES[track.category];
            const Icon = style?.icon ?? BookOpen;
            return (
              <a
                key={track.title}
                href={track.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group block"
              >
                <Card className="h-full transition-shadow hover:shadow-md">
                  <CardHeader>
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 space-y-1">
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-base group-hover:text-primary transition-colors">
                            {track.title}
                          </CardTitle>
                          <ExternalLink className="h-3.5 w-3.5 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
                        </div>
                        <CardDescription>{track.description}</CardDescription>
                      </div>
                      {hasSkills && (
                        <div className="flex shrink-0 flex-col items-center">
                          <div
                            className={`flex h-11 w-11 items-center justify-center rounded-full text-sm font-bold ${
                              track.score >= 60
                                ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300"
                                : track.score >= 30
                                  ? "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300"
                                  : "bg-muted text-muted-foreground"
                            }`}
                          >
                            {track.score}%
                          </div>
                          <span className="mt-0.5 text-[10px] text-muted-foreground">
                            match
                          </span>
                        </div>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge variant="outline" className={style?.color}>
                        <Icon className="h-3 w-3" />
                        {track.category}
                      </Badge>
                      <Badge variant="secondary">{track.primaryTech}</Badge>
                      <span className="text-xs text-muted-foreground">
                        {track.courses}
                      </span>
                      {track.partner && (
                        <Badge
                          variant="outline"
                          className="border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300"
                        >
                          {track.partner}
                        </Badge>
                      )}
                    </div>
                    {hasSkills && track.matched.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {track.matched.map((kw) => (
                          <span
                            key={kw}
                            className="inline-flex items-center gap-0.5 rounded-md bg-emerald-50 px-1.5 py-0.5 text-[11px] text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300"
                          >
                            <CheckCircle2 className="h-2.5 w-2.5" />
                            {kw}
                          </span>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </a>
            );
          })}
        </div>
      )}
    </div>
  );
}
