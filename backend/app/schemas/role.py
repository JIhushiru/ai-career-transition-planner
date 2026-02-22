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
