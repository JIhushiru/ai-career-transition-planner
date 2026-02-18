import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileText, Tags, Compass, Route, GraduationCap } from "lucide-react";

const features = [
  {
    icon: FileText,
    title: "Resume Parser",
    description:
      "Upload your PDF resume or paste text to extract skills, experience, and qualifications automatically.",
    href: "/resume",
    available: true,
  },
  {
    icon: Tags,
    title: "Skill Extraction",
    description:
      "AI-powered skill identification using NLP. Review, confirm, and edit your extracted skill profile.",
    href: "/skills",
    available: true,
  },
  {
    icon: Compass,
    title: "Career Explorer",
    description:
      "Discover matching career roles ranked by fit score using embeddings similarity and meta-model scoring.",
    href: "/explore",
    available: false,
  },
  {
    icon: Route,
    title: "Career GPS",
    description:
      "Multi-step career transition paths with difficulty scoring, timelines, and skill requirements.",
    href: "/transitions",
    available: false,
  },
  {
    icon: GraduationCap,
    title: "Learning Roadmap",
    description:
      "Personalized skill gap analysis with course recommendations, certifications, and milestones.",
    href: "/roadmap",
    available: false,
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto max-w-5xl px-6 py-16">
        <div className="mb-12 text-center">
          <h1 className="mb-4 text-4xl font-bold tracking-tight">
            AI Career Transition Planner
          </h1>
          <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
            Intelligent career planning powered by a hybrid AI meta-model.
            Upload your resume, discover matching roles, and chart your
            transition path.
          </p>
          <div className="mt-6 flex justify-center gap-3">
            <Button asChild size="lg">
              <Link href="/resume">Get Started</Link>
            </Button>
          </div>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card
                key={feature.title}
                className={!feature.available ? "opacity-50" : ""}
              >
                <CardHeader>
                  <div className="mb-2 flex items-center gap-2">
                    <Icon className="h-5 w-5 text-primary" />
                    <CardTitle className="text-base">{feature.title}</CardTitle>
                  </div>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  {feature.available ? (
                    <Button variant="outline" size="sm" asChild>
                      <Link href={feature.href}>Open</Link>
                    </Button>
                  ) : (
                    <span className="text-xs text-muted-foreground">
                      Coming soon
                    </span>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </main>
  );
}
