"""Career matching, transition paths, and roadmap endpoints."""

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.v1.roles import _role_to_response
from app.models.career_graph import UserMatch
from app.models.resume import Resume
from app.models.role import Role
from app.models.user import User
from app.schemas.role import (
    CareerPathsResponse,
    MatchResultsResponse,
    RoadmapResponse,
    RoleResponse,
    SkillGap,
    TransitionPathResponse,
    TransitionPathStep,
    UserMatchResponse,
)
from app.services.career_graph import CareerGraphService
from app.services.embedding_service import EmbeddingService
from app.services.matching_service import MatchingService
from app.services.meta_model import MetaModelScorer
from app.services.roadmap_generator import RoadmapGenerator

router = APIRouter(prefix="/career", tags=["career"])

meta_model = MetaModelScorer()
graph_service = CareerGraphService()
roadmap_gen = RoadmapGenerator()
embedding_service = EmbeddingService()


class MatchRequest(BaseModel):
    user_id: int
    resume_id: int | None = None
    career_mode: str = "growth"
    years_experience: int | None = None
    use_llm: bool = True
    top_k: int = Field(default=15, ge=1, le=50)


class TransitionRequest(BaseModel):
    user_id: int
    target_role_id: int
    max_steps: int = Field(default=3, ge=1, le=5)


class RoadmapRequest(BaseModel):
    user_id: int
    target_role_id: int
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

    scored = await meta_model.score_matches(
        db,
        user_id=body.user_id,
        resume_text=resume.raw_text,
        user_years=body.years_experience,
        career_mode=body.career_mode,
        top_k=body.top_k,
        use_llm=body.use_llm,
    )

    matches = []
    for s in scored:
        role = s["role"]
        matches.append(
            UserMatchResponse(
                role=_role_to_response(role),
                meta_score=s["meta_score"],
                breakdown=s["breakdown"],
                explanation=s.get("explanation"),
                matched_skills=s.get("matched_skills", []),
                missing_skills=s.get("missing_required", []),
            )
        )

    return MatchResultsResponse(matches=matches, user_id=body.user_id)


@router.get("/match/{user_id}/results", response_model=MatchResultsResponse)
async def get_cached_matches(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve previously computed match results."""
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
            )
        )

    return MatchResultsResponse(matches=matches, user_id=user_id)


@router.post("/transition-paths", response_model=CareerPathsResponse)
async def find_transition_paths(
    body: TransitionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Find multi-step career transition paths to a target role."""
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
        db, start_role_id, body.target_role_id, max_steps=body.max_steps
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
