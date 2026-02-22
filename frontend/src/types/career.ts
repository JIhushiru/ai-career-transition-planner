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
