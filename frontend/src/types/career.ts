export interface RoleResponse {
  id: number;
  title: string;
  title_ph: string | null;
  category: string | null;
  description: string | null;
  required_skills: string[];
  preferred_skills: string[];
  salary_range_ph: string | null;
  salary_range_usd: string | null;
  salary_min_ph: number | null;
  salary_max_ph: number | null;
  seniority: string | null;
  min_years_experience: number | null;
  demand_score: number | null;
  stability_score: number | null;
  growth_potential: number | null;
  remote_friendly: boolean | null;
}

export interface RoleListResponse {
  roles: RoleResponse[];
  total: number;
}

export interface CategoryCount {
  category: string;
  count: number;
}

export interface UserMatchResponse {
  role: RoleResponse;
  meta_score: number;
  breakdown: {
    embedding_score: number | null;
    skill_overlap_score: number | null;
    experience_match_score: number | null;
    llm_score: number | null;
    market_score: number | null;
  };
  explanation: string | null;
  matched_skills: string[];
  missing_skills: string[];
  salary_increase_min: number | null;
  salary_increase_max: number | null;
  salary_increase_pct: number | null;
}

export interface MatchResultsResponse {
  matches: UserMatchResponse[];
  user_id: number;
}

export interface TransitionPathStep {
  from_role: RoleResponse;
  to_role: RoleResponse;
  skills_needed: string[];
  months: number | null;
  difficulty: number;
}

export interface TransitionPathResponse {
  steps: TransitionPathStep[];
  total_months: number | null;
  total_difficulty: number;
}

export interface CareerPathsResponse {
  paths: TransitionPathResponse[];
  target_role: RoleResponse;
}

export interface LearningResource {
  title: string;
  url: string;
}

export interface SkillGap {
  skill: string;
  priority: string;
  estimated_hours: number | null;
  resources: LearningResource[];
}

export interface Milestone {
  phase: number;
  title: string;
  description: string;
  skills: string[];
  estimated_hours: number;
  estimated_weeks: number;
}

export interface RoadmapResponse {
  target_role: RoleResponse;
  skill_gaps: SkillGap[];
  total_estimated_hours: number | null;
  milestones: Milestone[];
}

// --- Dream Job Planner ---

export interface DreamJobPlanResponse {
  dream_role: {
    id: number;
    title: string;
    category: string;
    description: string;
    salary_range_ph: string | null;
    salary_range_usd: string | null;
    seniority: string;
    demand_score: number | null;
    growth_potential: number | null;
  };
  career_paths: {
    steps: {
      from_role: string;
      to_role: string;
      difficulty: number;
      months: number;
      upskills: string[];
      type: string;
    }[];
    total_months: number;
    total_difficulty: number;
  }[];
  skill_analysis: {
    current_skills: string[];
    skills_matched: string[];
    skills_to_learn: {
      skill: string;
      priority: string;
      estimated_hours: number;
    }[];
    match_percentage: number;
    total_learning_hours: number;
  };
  weekly_plan: {
    week: number;
    week_end?: number;
    week_label?: string;
    start_date: string;
    phase: string;
    focus_skills: string[];
    hours: number;
    hours_per_week?: number;
    actions: string[];
  }[];
  interview_prep: {
    behavioral_questions: string[];
    technical_topics: {
      skill: string;
      strength: string;
      prep_tip: string;
    }[];
    role_specific_areas: string[];
    preparation_tips: string[];
  };
  portfolio_projects: {
    title: string;
    description: string;
    skills_demonstrated: string[];
    complexity: string;
    estimated_hours: number;
  }[];
  milestones: Milestone[];
}

// --- Self-Assessment ---

export interface AssessmentQuestion {
  skill: string;
  importance: string;
  question: string;
  category?: string;
  scale: Record<string, string>;
}

export interface AssessmentQuestionsResponse {
  questions: AssessmentQuestion[];
  target_role_id: number | null;
}

// --- Role Insights ---

export interface DayInLifeResponse {
  role_id: number;
  role_title: string;
  source: string;
  schedule: { time: string; activity: string }[];
  daily_tools: string[];
  team_interactions: string[];
  challenges: string[];
  rewards: string[];
}

export interface RoleComparisonResponse {
  role_a: { id: number; title: string; category: string };
  role_b: { id: number; title: string; category: string };
  comparison: {
    salary: { a: string | null; b: string | null; higher: string };
    seniority: { a: string | null; b: string | null };
    experience_required: { a: number | null; b: number | null };
    demand: { a: number | null; b: number | null; higher: string };
    growth_potential: { a: number | null; b: number | null; higher: string };
    remote_friendly: { a: boolean | null; b: boolean | null };
    shared_skills: string[];
    unique_to_a: string[];
    unique_to_b: string[];
    skill_transferability: number;
  };
}
