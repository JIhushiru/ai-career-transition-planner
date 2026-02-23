"""Career matching, transition paths, and roadmap endpoints."""

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.api.v1.roles import _role_to_response
from app.models.career_graph import UserMatch
from app.models.resume import Resume
from app.models.role import Role
from app.models.user import User
from app.schemas.role import (
    AssessmentQuestionsResponse,
    AssessmentRequest,
    AssessmentResponse,
    CareerPathsResponse,
    DayInLifeResponse,
    DreamJobPlanResponse,
    DreamJobRequest,
    MatchResultsResponse,
    RoadmapResponse,
    RoleComparisonResponse,
    RoleResponse,
    SkillGap,
    TransitionPathResponse,
    TransitionPathStep,
    UserMatchResponse,
)
from app.services.career_graph import CareerGraphService
from app.services.dream_job_planner import DreamJobPlanner
from app.services.embedding_service import EmbeddingService
from app.services.matching_service import MatchingService
from app.services.meta_model import MetaModelScorer
from app.services.roadmap_generator import RoadmapGenerator
from app.services.role_insights import RoleInsightsService
from app.services.self_assessment import SelfAssessmentService

router = APIRouter(prefix="/career", tags=["career"])

meta_model = MetaModelScorer()
graph_service = CareerGraphService()
roadmap_gen = RoadmapGenerator()
embedding_service = EmbeddingService()
dream_planner = DreamJobPlanner()
assessment_service = SelfAssessmentService()
insights_service = RoleInsightsService()


class MatchRequest(BaseModel):
    user_id: int
    resume_id: int | None = None
    career_mode: str = "growth"
    years_experience: int | None = Field(default=None, ge=0, le=100)
    current_salary: int | None = Field(default=None, ge=0)
    use_llm: bool = True
    top_k: int = Field(default=15, ge=1, le=50)


class TransitionRequest(BaseModel):
    user_id: int
    target_role_id: int
    resume_id: int | None = None


class RoadmapRequest(BaseModel):
    user_id: int
    target_role_id: int
    resume_id: int | None = None
    include_resources: bool = False


class EmbeddingsRequest(BaseModel):
    confirm: bool = True


@router.post("/match", response_model=MatchResultsResponse)
async def compute_matches(
    body: MatchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Run the full meta-model scoring pipeline for a user."""
    # Verify user exists and has a resume
    result = await db.execute(select(User).where(User.id == body.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    if body.resume_id:
        result = await db.execute(
            select(Resume).where(
                Resume.id == body.resume_id,
                Resume.user_id == body.user_id,
            )
        )
        resume = result.scalar_one_or_none()
        if not resume:
            raise HTTPException(404, "Resume not found or does not belong to this user.")
    else:
        result = await db.execute(
            select(Resume)
            .where(Resume.user_id == body.user_id)
            .order_by(Resume.created_at.desc())
            .limit(1)
        )
        resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(400, "No resume found for user. Upload a resume first.")

    # Check if roles have embeddings
    result = await db.execute(select(Role).where(Role.embedding.isnot(None)).limit(1))
    if not result.scalar_one_or_none():
        raise HTTPException(
            400,
            "Role embeddings not computed yet. POST /api/v1/career/embeddings first.",
        )

    # Resolve salary: prefer request body, fall back to user profile
    user_salary = body.current_salary or user.current_salary

    scored = await meta_model.score_matches(
        db,
        user_id=body.user_id,
        resume_text=resume.raw_text,
        user_years=body.years_experience,
        career_mode=body.career_mode,
        top_k=body.top_k,
        use_llm=body.use_llm,
        user_salary=user_salary,
    )

    matches = []
    for s in scored:
        role = s["role"]
        role_resp = _role_to_response(role)

        # Compute salary deltas if user salary is known
        sal_inc_min = sal_inc_max = sal_inc_pct = None
        if user_salary and role.salary_min_ph:
            sal_inc_min = role.salary_min_ph - user_salary
            sal_inc_max = (role.salary_max_ph or role.salary_min_ph) - user_salary
            midpoint = ((role.salary_min_ph or 0) + (role.salary_max_ph or role.salary_min_ph)) // 2
            sal_inc_pct = round(((midpoint - user_salary) / user_salary) * 100, 1) if user_salary > 0 else None

        matches.append(
            UserMatchResponse(
                role=role_resp,
                meta_score=s["meta_score"],
                breakdown=s["breakdown"],
                explanation=s.get("explanation"),
                matched_skills=s.get("matched_skills", []),
                missing_skills=s.get("missing_required", []),
                salary_increase_min=sal_inc_min,
                salary_increase_max=sal_inc_max,
                salary_increase_pct=sal_inc_pct,
            )
        )

    return MatchResultsResponse(matches=matches, user_id=body.user_id)


def _compute_salary_deltas(role: Role, user_salary: int | None):
    """Compute salary increase fields relative to user's current salary."""
    if not user_salary or not role.salary_min_ph:
        return None, None, None
    sal_inc_min = role.salary_min_ph - user_salary
    sal_inc_max = (role.salary_max_ph or role.salary_min_ph) - user_salary
    midpoint = ((role.salary_min_ph or 0) + (role.salary_max_ph or role.salary_min_ph)) // 2
    sal_inc_pct = round(((midpoint - user_salary) / user_salary) * 100, 1) if user_salary > 0 else None
    return sal_inc_min, sal_inc_max, sal_inc_pct


@router.get("/match/{user_id}/results", response_model=MatchResultsResponse)
async def get_cached_matches(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve previously computed match results."""
    if current_user.id != user_id:
        raise HTTPException(403, "Not authorized to access another user's matches")
    user_salary = current_user.current_salary

    result = await db.execute(
        select(UserMatch, Role)
        .join(Role, UserMatch.role_id == Role.id)
        .where(UserMatch.user_id == user_id)
        .order_by(UserMatch.meta_score.desc())
    )
    rows = result.all()

    if not rows:
        raise HTTPException(404, "No match results found. Run /career/match first.")

    matches = []
    for match, role in rows:
        sal_inc_min, sal_inc_max, sal_inc_pct = _compute_salary_deltas(role, user_salary)
        matches.append(
            UserMatchResponse(
                role=_role_to_response(role),
                meta_score=match.meta_score or 0.0,
                breakdown={
                    "embedding_score": match.embedding_score,
                    "skill_overlap_score": match.skill_overlap_score,
                    "experience_match_score": match.experience_match_score,
                    "llm_score": match.llm_score,
                    "market_score": match.market_score,
                },
                explanation=match.explanation,
                salary_increase_min=sal_inc_min,
                salary_increase_max=sal_inc_max,
                salary_increase_pct=sal_inc_pct,
            )
        )

    return MatchResultsResponse(matches=matches, user_id=user_id)


@router.get("/quick-wins/{user_id}", response_model=list[UserMatchResponse])
async def get_quick_wins(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get high-match roles that pay more than the user's current salary."""
    if current_user.id != user_id:
        raise HTTPException(403, "Not authorized to access another user's data")
    user = current_user

    if not user.current_salary:
        return []

    result = await db.execute(
        select(UserMatch, Role)
        .join(Role, UserMatch.role_id == Role.id)
        .where(
            UserMatch.user_id == user_id,
            UserMatch.meta_score >= 0.5,
            Role.salary_min_ph > user.current_salary,
        )
        .order_by(Role.salary_max_ph.desc())
        .limit(5)
    )
    rows = result.all()

    wins = []
    for match, role in rows:
        sal_inc_min, sal_inc_max, sal_inc_pct = _compute_salary_deltas(role, user.current_salary)
        wins.append(
            UserMatchResponse(
                role=_role_to_response(role),
                meta_score=match.meta_score or 0.0,
                breakdown={
                    "embedding_score": match.embedding_score,
                    "skill_overlap_score": match.skill_overlap_score,
                    "experience_match_score": match.experience_match_score,
                    "llm_score": match.llm_score,
                    "market_score": match.market_score,
                },
                explanation=match.explanation,
                salary_increase_min=sal_inc_min,
                salary_increase_max=sal_inc_max,
                salary_increase_pct=sal_inc_pct,
            )
        )

    return wins


@router.post("/transition-paths", response_model=CareerPathsResponse)
async def find_transition_paths(
    body: TransitionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Find multi-step career transition paths to a target role."""
    # Validate resume exists
    if body.resume_id:
        result = await db.execute(
            select(Resume).where(
                Resume.id == body.resume_id,
                Resume.user_id == body.user_id,
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(404, "Resume not found or does not belong to this user.")
    else:
        result = await db.execute(
            select(Resume).where(Resume.user_id == body.user_id).limit(1)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(400, "No resume found. Upload a resume first.")

    # Find user's best-match current role
    result = await db.execute(
        select(UserMatch)
        .where(UserMatch.user_id == body.user_id)
        .order_by(UserMatch.meta_score.desc())
        .limit(1)
    )
    best_match = result.scalar_one_or_none()
    if not best_match:
        raise HTTPException(400, "Run /career/match first to establish your current role fit.")

    start_role_id = best_match.role_id

    # Get target role
    result = await db.execute(select(Role).where(Role.id == body.target_role_id))
    target_role = result.scalar_one_or_none()
    if not target_role:
        raise HTTPException(404, "Target role not found")

    paths = await graph_service.find_paths(
        db, start_role_id, body.target_role_id, max_steps=5
    )
    role_map = await graph_service.get_role_map(db)

    response_paths = []
    for path in paths:
        steps = []
        total_months = 0
        total_diff = 0.0

        for step in path:
            from_role = role_map.get(step["from_role_id"])
            to_role = role_map.get(step["to_role_id"])
            if not from_role or not to_role:
                continue

            months = step.get("months", 12)
            diff = step.get("difficulty", 0.5)
            total_months += months
            total_diff += diff

            steps.append(
                TransitionPathStep(
                    from_role=_role_to_response(from_role),
                    to_role=_role_to_response(to_role),
                    skills_needed=step.get("upskills", []),
                    months=months,
                    difficulty=diff,
                )
            )

        if steps:
            response_paths.append(
                TransitionPathResponse(
                    steps=steps,
                    total_months=total_months,
                    total_difficulty=round(total_diff / len(steps), 3) if steps else 0,
                )
            )

    # Fallback: if no graph paths found, generate a direct transition
    if not response_paths and start_role_id != body.target_role_id:
        start_role = role_map.get(start_role_id)
        if start_role and target_role:
            # Compute skill gap as upskills
            from app.api.v1.roles import _safe_json_loads

            target_required = _safe_json_loads(target_role.required_skills)
            start_skills = {s.lower() for s in _safe_json_loads(start_role.required_skills)}
            skills_needed = [s for s in target_required if s.lower() not in start_skills]

            # Estimate difficulty based on skill gap
            gap_ratio = len(skills_needed) / max(len(target_required), 1)
            difficulty = round(0.3 + gap_ratio * 0.6, 2)
            months = max(6, int(len(skills_needed) * 2.5))

            response_paths.append(
                TransitionPathResponse(
                    steps=[
                        TransitionPathStep(
                            from_role=_role_to_response(start_role),
                            to_role=_role_to_response(target_role),
                            skills_needed=skills_needed,
                            months=months,
                            difficulty=difficulty,
                        )
                    ],
                    total_months=months,
                    total_difficulty=difficulty,
                )
            )

    return CareerPathsResponse(
        paths=response_paths,
        target_role=_role_to_response(target_role),
    )


@router.post("/roadmap", response_model=RoadmapResponse)
async def generate_roadmap(
    body: RoadmapRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate skill gap analysis and learning roadmap."""
    # Validate resume exists
    if body.resume_id:
        result = await db.execute(
            select(Resume).where(
                Resume.id == body.resume_id,
                Resume.user_id == body.user_id,
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(404, "Resume not found or does not belong to this user.")
    else:
        result = await db.execute(
            select(Resume).where(Resume.user_id == body.user_id).limit(1)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(400, "No resume found. Upload a resume first.")

    analysis = await roadmap_gen.analyze_skill_gaps(
        db, body.user_id, body.target_role_id
    )

    if "error" in analysis:
        raise HTTPException(404, analysis["error"])

    gaps = analysis["skill_gaps"]

    if body.include_resources:
        gaps = await roadmap_gen.enrich_with_resources(gaps)

    role = analysis["role"]
    return RoadmapResponse(
        target_role=_role_to_response(role),
        skill_gaps=[
            SkillGap(
                skill=g["skill"],
                priority=g["priority"],
                estimated_hours=g["estimated_hours"],
                resources=g.get("resources", []),
            )
            for g in gaps
        ],
        total_estimated_hours=analysis["total_estimated_hours"],
        milestones=analysis["milestones"],
    )


@router.post("/embeddings")
async def compute_embeddings(
    body: EmbeddingsRequest,
    db: AsyncSession = Depends(get_db),
):
    """Pre-compute embeddings for all roles. Run after seeding."""
    count = await embedding_service.compute_role_embeddings(db)
    return {"message": f"Computed embeddings for {count} roles"}


# --- Dream Job Planner ---


@router.post("/dream-job", response_model=DreamJobPlanResponse)
async def plan_dream_job(
    body: DreamJobRequest,
    db: AsyncSession = Depends(get_db),
):
    """Build a complete reverse-engineered plan to reach a dream role.

    Returns career paths, skill gaps, weekly action plan, interview prep,
    and portfolio project suggestions.
    """
    result = await db.execute(select(User).where(User.id == body.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    # Validate resume exists
    if body.resume_id:
        result = await db.execute(
            select(Resume).where(
                Resume.id == body.resume_id,
                Resume.user_id == body.user_id,
            )
        )
        resume = result.scalar_one_or_none()
        if not resume:
            raise HTTPException(404, "Resume not found or does not belong to this user.")
    else:
        result = await db.execute(
            select(Resume)
            .where(Resume.user_id == body.user_id)
            .order_by(Resume.created_at.desc())
            .limit(1)
        )
        resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(400, "No resume found. Upload a resume first.")

    # Resolve current role: from request, from best match, or None
    current_role_id = body.current_role_id
    if not current_role_id:
        match_result = await db.execute(
            select(UserMatch)
            .where(UserMatch.user_id == body.user_id)
            .order_by(UserMatch.meta_score.desc())
            .limit(1)
        )
        best_match = match_result.scalar_one_or_none()
        if best_match:
            current_role_id = best_match.role_id

    salary = body.current_salary or user.current_salary

    plan = await dream_planner.build_plan(
        db,
        user_id=body.user_id,
        dream_role_id=body.dream_role_id,
        current_role_id=current_role_id,
        user_years=body.years_experience,
        current_salary=salary,
    )

    if "error" in plan:
        raise HTTPException(404, plan["error"])

    return DreamJobPlanResponse(**plan)


# --- Self-Assessment ---


@router.get("/assessment/questions", response_model=AssessmentQuestionsResponse)
async def get_assessment_questions(
    target_role_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get skill assessment questions, optionally tailored to a target role."""
    questions = await assessment_service.get_assessment_questions(
        db, target_role_id=target_role_id
    )
    return AssessmentQuestionsResponse(
        questions=questions,
        target_role_id=target_role_id,
    )


@router.post("/assessment", response_model=AssessmentResponse)
async def submit_assessment(
    body: AssessmentRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit skill self-assessment ratings. Merges with existing skills."""
    result = await db.execute(select(User).where(User.id == body.user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(404, "User not found")

    ratings = [r.model_dump() for r in body.ratings]
    saved = await assessment_service.save_assessment(db, body.user_id, ratings)
    return AssessmentResponse(**saved)


# --- Role Insights ---


@router.get("/roles/{role_id}/day-in-life", response_model=DayInLifeResponse)
async def get_day_in_life(
    role_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a 'day in the life' description for a role."""
    result = await insights_service.get_day_in_life(db, role_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return DayInLifeResponse(**result)


@router.get("/roles/compare", response_model=RoleComparisonResponse)
async def compare_roles(
    role_a: int = Query(..., description="First role ID"),
    role_b: int = Query(..., description="Second role ID"),
    db: AsyncSession = Depends(get_db),
):
    """Compare two roles side by side."""
    result = await insights_service.compare_roles(db, role_a, role_b)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return RoleComparisonResponse(**result)


# --- Success Stories ---


@router.get("/stories/{user_id}")
async def get_success_stories(
    user_id: int,
    target_role_id: int = Query(..., description="Target role ID"),
    count: int = Query(3, ge=1, le=5),
    db: AsyncSession = Depends(get_db),
):
    """Get 'People Like You' success story templates for a target role."""
    result = await db.execute(select(User).where(User.id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(404, "User not found")

    # Validate user has a resume
    result = await db.execute(
        select(Resume).where(Resume.user_id == user_id).limit(1)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(400, "No resume found. Upload a resume first.")

    stories = await stories_service.generate_stories(
        db, user_id, target_role_id, count=count
    )
    return {"stories": stories, "target_role_id": target_role_id}
