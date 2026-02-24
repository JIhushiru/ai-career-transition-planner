from pydantic import BaseModel, Field


class ExtractedSkill(BaseModel):
    name: str
    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: str


class ParsedSections(BaseModel):
    contact: dict = Field(default_factory=dict)
    summary: str = ""
    experience: list[dict] = Field(default_factory=list)
    education: list[dict] = Field(default_factory=list)
    skills_section: list[str] = Field(default_factory=list)
    events: list[str] = Field(default_factory=list)


class ResumeUploadResponse(BaseModel):
    user_id: int
    resume_id: int
    raw_text: str
    skills: list[ExtractedSkill]
    parsed_sections: ParsedSections
    estimated_years_experience: int | None = None


class ResumeTextRequest(BaseModel):
    text: str = Field(min_length=10, max_length=50000)


class ResumeResponse(BaseModel):
    id: int
    filename: str | None
    raw_text: str
    source_type: str
    skills: list[ExtractedSkill]
    parsed_sections: ParsedSections


class SkillUpdateRequest(BaseModel):
    add: list[str] = Field(default_factory=list)
    remove: list[int] = Field(default_factory=list)
    confirm: list[int] = Field(default_factory=list)


class SkillsResponse(BaseModel):
    skills: list[ExtractedSkill]
    categories: dict[str, list[ExtractedSkill]] = Field(default_factory=dict)


class ResumeListItem(BaseModel):
    id: int
    filename: str | None
    source_type: str
    created_at: str
    skill_count: int


class ResumeListResponse(BaseModel):
    resumes: list[ResumeListItem]


class SessionResponse(BaseModel):
    session_id: str
    user_id: int
