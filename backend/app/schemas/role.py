from pydantic import BaseModel, Field


class RoleResponse(BaseModel):
    id: int
    title: str
    title_ph: str | None = None
    category: str | None = None
    description: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    salary_range_ph: str | None = None
    salary_range_usd: str | None = None
    salary_min_ph: int | None = None
    salary_max_ph: int | None = None
    seniority: str | None = None
    min_years_experience: int | None = None
    demand_score: float | None = None
    stability_score: float | None = None
    growth_potential: float | None = None
    remote_friendly: bool | None = None


class RoleListResponse(BaseModel):
    roles: list[RoleResponse]
    total: int


class TransitionResponse(BaseModel):
    id: int
    from_role: RoleResponse
    to_role: RoleResponse
    difficulty: float
    typical_months: int | None = None
    required_upskills: list[str] = Field(default_factory=list)
    market_viability: float
    transition_type: str | None = None


class UserMatchResponse(BaseModel):
    role: RoleResponse
    meta_score: float
    breakdown: dict[str, float | None]
    explanation: str | None = None
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    salary_increase_min: int | None = None
    salary_increase_max: int | None = None
    salary_increase_pct: float | None = None


class MatchResultsResponse(BaseModel):
    matches: list[UserMatchResponse]
    user_id: int


class TransitionPathStep(BaseModel):
    from_role: RoleResponse
    to_role: RoleResponse
    skills_needed: list[str] = Field(default_factory=list)
    months: int | None = None
    difficulty: float


class TransitionPathResponse(BaseModel):
    steps: list[TransitionPathStep]
    total_months: int | None = None
    total_difficulty: float


class CareerPathsResponse(BaseModel):
    paths: list[TransitionPathResponse]
    target_role: RoleResponse


class LearningResource(BaseModel):
    title: str
    url: str = ""


class SkillGap(BaseModel):
    skill: str
    priority: str
    estimated_hours: int | None = None
    resources: list[LearningResource] = Field(default_factory=list)


class RoadmapResponse(BaseModel):
    target_role: RoleResponse
    skill_gaps: list[SkillGap]
    total_estimated_hours: int | None = None
    milestones: list[dict] = Field(default_factory=list)


# --- Dream Job Planner ---


class DreamJobRequest(BaseModel):
    user_id: int
    dream_role_id: int
    resume_id: int | None = None
    current_role_id: int | None = None
    years_experience: int | None = None
    current_salary: int | None = None


class DreamJobPlanResponse(BaseModel):
    dream_role: dict
    career_paths: list[dict] = Field(default_factory=list)
    skill_analysis: dict
    weekly_plan: list[dict] = Field(default_factory=list)
    interview_prep: dict
    portfolio_projects: list[dict] = Field(default_factory=list)
    milestones: list[dict] = Field(default_factory=list)


# --- Self-Assessment ---


class AssessmentRating(BaseModel):
    skill: str
    rating: int = Field(ge=0, le=4)
    category: str | None = None


class AssessmentRequest(BaseModel):
    user_id: int
    ratings: list[AssessmentRating]


class AssessmentResponse(BaseModel):
    added: int
    updated: int
    total: int


class AssessmentQuestionsResponse(BaseModel):
    questions: list[dict]
    target_role_id: int | None = None


# --- Role Insights ---


class DayInLifeResponse(BaseModel):
    role_id: int
    role_title: str
    source: str
    schedule: list[dict] = Field(default_factory=list)
    daily_tools: list[str] = Field(default_factory=list)
    team_interactions: list[str] = Field(default_factory=list)
    challenges: list[str] = Field(default_factory=list)
    rewards: list[str] = Field(default_factory=list)


class RoleComparisonResponse(BaseModel):
    role_a: dict
    role_b: dict
    comparison: dict
