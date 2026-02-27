"use client";

import { useState, useMemo } from "react";
import { Search, ExternalLink, BookOpen, Code, Database, BarChart3, Brain, Server, FlaskConical } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

interface CareerTrack {
  title: string;
  description: string;
  courses: string;
  category: string;
  primaryTech: string;
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
    url: "https://www.datacamp.com/tracks/associate-data-analyst-in-sql",
  },
  {
    title: "Associate Data Scientist in Python",
    description: "Learn data science in Python, from data manipulation to machine learning. This track provides the skills needed to succeed as a data scientist!",
    courses: "19 Courses and Projects",
    category: "Data Science",
    primaryTech: "Python",
    url: "https://www.datacamp.com/tracks/associate-data-scientist-in-python",
  },
  {
    title: "Data Analyst in Power BI",
    description: "Co-created with Microsoft\u2014gain the Power BI skills you need to prepare, model, and visualize data for the PL-300 Data Analyst certification.",
    courses: "17 Courses and Projects",
    category: "Data Analysis",
    primaryTech: "Power BI",
    partner: "Microsoft",
    url: "https://www.datacamp.com/tracks/data-analyst-in-power-bi",
  },
  {
    title: "Data Analyst in Python",
    description: "Develop your data analytics skills in Python. Gain the data analyst skills to manipulate, analyze, and visualize data. No coding experience required!",
    courses: "14 Courses and Projects",
    category: "Data Analysis",
    primaryTech: "Python",
    url: "https://www.datacamp.com/tracks/data-analyst-in-python",
  },
  {
    title: "Associate Data Engineer in SQL",
    description: "Learn the fundamentals of data engineering: database design and data warehousing, working with technologies including PostgreSQL and Snowflake!",
    courses: "11 Courses and Projects",
    category: "Data Engineering",
    primaryTech: "SQL",
    url: "https://www.datacamp.com/tracks/associate-data-engineer-in-sql",
  },
  {
    title: "Data Engineer in Python",
    description: "Gain in-demand skills to efficiently ingest, clean, manage data, and schedule and monitor pipelines, setting you apart in the data engineering field.",
    courses: "17 Courses and Projects",
    category: "Data Engineering",
    primaryTech: "Python",
    url: "https://www.datacamp.com/tracks/data-engineer-in-python",
  },
  {
    title: "Associate AI Engineer for Data Scientists",
    description: "Train and fine-tune the latest AI models for production, including LLMs like Llama 3. Start your journey to becoming an AI Engineer today!",
    courses: "11 Courses and Projects",
    category: "AI & ML",
    primaryTech: "Python",
    url: "https://www.datacamp.com/tracks/associate-ai-engineer-for-data-scientists",
  },
  {
    title: "Associate Data Scientist in R",
    description: "Learn how to use R for data science, from data manipulation to machine learning. Gain the career-building skills you need to succeed in data science!",
    courses: "26 Courses and Projects",
    category: "Data Science",
    primaryTech: "R",
    url: "https://www.datacamp.com/tracks/associate-data-scientist-in-r",
  },
  {
    title: "Data Scientist in Python",
    description: "Learn data science in Python, from data manipulation to machine learning, and gain the skills needed for the Data Scientist in Python certification!",
    courses: "11 Courses and Projects",
    category: "Data Science",
    primaryTech: "Python",
    url: "https://www.datacamp.com/tracks/data-scientist-in-python",
  },
  {
    title: "Data Analyst in Tableau",
    description: "Master Tableau for data analysis and develop your skills in one of the world's most popular BI tools. No prior experience is required.",
    courses: "9 Courses and Projects",
    category: "Data Analysis",
    primaryTech: "Tableau",
    url: "https://www.datacamp.com/tracks/data-analyst-in-tableau",
  },
  {
    title: "Data Analyst in R",
    description: "From exploratory data analysis with dplyr to data visualization with ggplot2\u2014gain the career-building R skills you need to succeed as a data analyst!",
    courses: "11 Courses and Projects",
    category: "Data Analysis",
    primaryTech: "R",
    url: "https://www.datacamp.com/tracks/data-analyst-in-r",
  },
  {
    title: "Microsoft Azure Developer Associate (AZ-204)",
    description: "Prepare for AZ-204 by building and integrating cloud applications on Microsoft Azure with hands-on, developer-focused courses.",
    courses: "7 Courses and Projects",
    category: "Cloud & DevOps",
    primaryTech: "Azure",
    partner: "Microsoft",
    url: "https://www.datacamp.com/tracks/microsoft-azure-developer-associate-az-204",
  },
  {
    title: "Data Scientist in R",
    description: "Learn data science with R, from data manipulation to machine learning, and gain the skills needed for the Data Scientist in R certification!",
    courses: "11 Courses and Projects",
    category: "Data Science",
    primaryTech: "R",
    url: "https://www.datacamp.com/tracks/data-scientist-in-r",
  },
  {
    title: "Associate AI Engineer for Developers",
    description: "Learn how to integrate AI into software applications using APIs and open-source libraries. Start your journey to becoming an AI Engineer today!",
    courses: "10 Courses and Projects",
    category: "AI & ML",
    primaryTech: "Python",
    url: "https://www.datacamp.com/tracks/associate-ai-engineer-for-developers",
  },
  {
    title: "Associate Python Developer",
    description: "Learn Python for software development, from writing functions to defining classes. Get the necessary skills to kickstart your developer career!",
    courses: "10 Courses and Projects",
    category: "Software Dev",
    primaryTech: "Python",
    url: "https://www.datacamp.com/tracks/associate-python-developer",
  },
  {
    title: "Machine Learning Scientist in Python",
    description: "Discover machine learning with Python and work towards becoming a machine learning scientist. Explore supervised, unsupervised, and deep learning.",
    courses: "24 Courses and Projects",
    category: "AI & ML",
    primaryTech: "Python",
    url: "https://www.datacamp.com/tracks/machine-learning-scientist-in-python",
  },
  {
    title: "Machine Learning Engineer",
    description: "This career track teaches you everything you need to know about machine learning engineering and MLOps.",
    courses: "15 Courses and Projects",
    category: "AI & ML",
    primaryTech: "Python",
    url: "https://www.datacamp.com/tracks/machine-learning-engineer",
  },
  {
    title: "Python Developer",
    description: "From testing code and implementing version control to web scraping and developing packages, take the next step in your Python developer journey!",
    courses: "8 Courses and Projects",
    category: "Software Dev",
    primaryTech: "Python",
    url: "https://www.datacamp.com/tracks/python-developer",
  },
  {
    title: "Data Analyst in Databricks",
    description: "Master Databricks, SQL, data visualization, and management in the Lakehouse Platform for the Databricks Data Analyst Associate certification.",
    courses: "9 Courses and Projects",
    category: "Data Analysis",
    primaryTech: "Databricks",
    url: "https://www.datacamp.com/tracks/data-analyst-in-databricks",
  },
  {
    title: "Professional Data Engineer in Python",
    description: "Dive deep into advanced skills and state-of-the-art tools revolutionizing data engineering roles today with our Professional Data Engineer track.",
    courses: "15 Courses and Projects",
    category: "Data Engineering",
    primaryTech: "Python",
    url: "https://www.datacamp.com/tracks/professional-data-engineer-in-python",
  },
  {
    title: "Associate Data Engineer in Snowflake",
    description: "Learn to design, query, and build in Snowflake - mastering Snowflake SQL for transformation and modeling to become a job-ready Data Engineer.",
    courses: "11 Courses and Projects",
    category: "Data Engineering",
    primaryTech: "Snowflake",
    partner: "Snowflake",
    url: "https://www.datacamp.com/tracks/associate-data-engineer-in-snowflake",
  },
  {
    title: "SQL Server Developer",
    description: "Gain the SQL Server skills you need to write, troubleshoot, and optimize your queries using SQL Server.",
    courses: "10 Courses and Projects",
    category: "Software Dev",
    primaryTech: "SQL",
    url: "https://www.datacamp.com/tracks/sql-server-developer",
  },
  {
    title: "Statistician in R",
    description: "A statistician collects and analyzes data and helps companies make sense of quantitative data, including spotting trends and making predictions.",
    courses: "14 Courses and Projects",
    category: "Data Science",
    primaryTech: "R",
    url: "https://www.datacamp.com/tracks/statistician-in-r",
  },
  {
    title: "R Developer",
    description: "Gain the career-building skills you need to succeed as an R Developer by learning to write and package code efficiently. No coding experience needed!",
    courses: "15 Courses and Projects",
    category: "Software Dev",
    primaryTech: "R",
    url: "https://www.datacamp.com/tracks/r-developer",
  },
  {
    title: "Quantitative Analyst in R",
    description: "Ensure portfolios are risk balanced, help find new trading opportunities, and evaluate asset prices using mathematical models.",
    courses: "15 Courses and Projects",
    category: "Data Science",
    primaryTech: "R",
    url: "https://www.datacamp.com/tracks/quantitative-analyst-in-r",
  },
  {
    title: "Machine Learning Scientist in R",
    description: "A machine learning scientist researches new approaches and builds machine learning models.",
    courses: "17 Courses and Projects",
    category: "AI & ML",
    primaryTech: "R",
    url: "https://www.datacamp.com/tracks/machine-learning-scientist-in-r",
  },
  {
    title: "Java Developer",
    description: "Master Java development from fundamentals to testing and optimization. Build applications that are reliable and ready to ship.",
    courses: "7 Courses and Projects",
    category: "Software Dev",
    primaryTech: "Java",
    url: "https://www.datacamp.com/tracks/java-developer",
  },
  {
    title: "Data Engineer in Java",
    description: "Develop essential Java skills for data engineering, from file processing and database integration to performance optimization.",
    courses: "9 Courses and Projects",
    category: "Data Engineering",
    primaryTech: "Java",
    url: "https://www.datacamp.com/tracks/data-engineer-in-java",
  },
];

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

export default function DataCampPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [selectedTech, setSelectedTech] = useState<string>("All");

  const filteredTracks = useMemo(() => {
    return CAREER_TRACKS.filter((track) => {
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
  }, [searchQuery, selectedCategory, selectedTech]);

  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = { All: CAREER_TRACKS.length };
    for (const track of CAREER_TRACKS) {
      counts[track.category] = (counts[track.category] || 0) + 1;
    }
    return counts;
  }, []);

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">
          DataCamp Career Tracks
        </h2>
        <p className="text-muted-foreground">
          Explore {CAREER_TRACKS.length} career tracks to find the right
          learning path for your goals. Filter by category, technology, or
          search by keyword.
        </p>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Find Your Track
          </CardTitle>
          <CardDescription>
            Not sure where to start? Filter by the career area or technology
            you're interested in.
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
        </CardContent>
      </Card>

      {/* Results count */}
      <p className="text-sm text-muted-foreground">
        Showing {filteredTracks.length} of {CAREER_TRACKS.length} tracks
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
                      <CardTitle className="text-base group-hover:text-primary transition-colors">
                        {track.title}
                      </CardTitle>
                      <ExternalLink className="h-4 w-4 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
                    </div>
                    <CardDescription>{track.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge
                        variant="outline"
                        className={style?.color}
                      >
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
