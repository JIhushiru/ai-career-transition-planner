import json
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, get_optional_user
from app.models.resume import Resume
from app.models.skill import Skill, UserSkill
from app.models.user import User
from app.schemas.resume import (
    ExtractedSkill,
    ParsedSections,
    ResumeListItem,
    ResumeListResponse,
    ResumeTextRequest,
    ResumeUploadResponse,
    SessionResponse,
    SkillsResponse,
)
from app.services.resume_parser import ResumeParser
from app.services.skill_extractor import SkillExtractor

router = APIRouter(prefix="/resume", tags=["resume"])

parser = ResumeParser()
extractor = SkillExtractor()


async def _get_or_create_user(db: AsyncSession, session_id: str | None = None) -> User:
    if session_id:
        result = await db.execute(select(User).where(User.session_id == session_id))
        user = result.scalar_one_or_none()
        if user:
            return user

    user = User(session_id=session_id or uuid.uuid4().hex)
    db.add(user)
    await db.flush()
    return user


async def _save_skills(
    db: AsyncSession,
    user: User,
    resume: Resume,
    extracted_skills: list[dict],
) -> list[ExtractedSkill]:
    saved_skills = []
    for skill_data in extracted_skills:
        result = await db.execute(
            select(Skill).where(Skill.name == skill_data["name"])
        )
        skill = result.scalar_one_or_none()
        if not skill:
            skill = Skill(name=skill_data["name"], category=skill_data["category"])
            db.add(skill)
            await db.flush()

        user_skill = UserSkill(
            user_id=user.id,
            skill_id=skill.id,
            resume_id=resume.id,
            confidence=skill_data["confidence"],
            source=skill_data["source"],
        )
        db.add(user_skill)

        saved_skills.append(
            ExtractedSkill(
                name=skill_data["name"],
                category=skill_data["category"],
                confidence=skill_data["confidence"],
                source=skill_data["source"],
            )
        )
    return saved_skills


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    auth_user: User | None = Depends(get_optional_user),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 10MB)")

    raw_text = parser.extract_text_from_pdf(contents)
    if not raw_text.strip():
        raise HTTPException(422, "Could not extract text from PDF")

    parsed_sections = parser.parse_sections(raw_text)
    extracted_skills = extractor.extract_skills(raw_text)
    estimated_years = parser.estimate_years_experience(raw_text)

    user = auth_user or await _get_or_create_user(db)
    resume = Resume(
        user_id=user.id,
        filename=file.filename,
        raw_text=raw_text,
        source_type="pdf",
        parsed_data=json.dumps(parsed_sections),
    )
    db.add(resume)
    await db.flush()

    if estimated_years and not user.years_experience:
        user.years_experience = estimated_years

    skills = await _save_skills(db, user, resume, extracted_skills)
    await db.commit()

    return ResumeUploadResponse(
        user_id=user.id,
        resume_id=resume.id,
        raw_text=raw_text,
        skills=skills,
        parsed_sections=ParsedSections(**parsed_sections),
        estimated_years_experience=estimated_years,
    )


@router.post("/parse-text", response_model=ResumeUploadResponse)
async def parse_text_resume(
    body: ResumeTextRequest,
    db: AsyncSession = Depends(get_db),
    auth_user: User | None = Depends(get_optional_user),
):
    parsed_sections = parser.parse_sections(body.text)
    extracted_skills = extractor.extract_skills(body.text)
    estimated_years = parser.estimate_years_experience(body.text)

    user = auth_user or await _get_or_create_user(db)
    resume = Resume(
        user_id=user.id,
        filename=None,
        raw_text=body.text,
        source_type="text_paste",
        parsed_data=json.dumps(parsed_sections),
    )
    db.add(resume)
    await db.flush()

    if estimated_years and not user.years_experience:
        user.years_experience = estimated_years

    skills = await _save_skills(db, user, resume, extracted_skills)
    await db.commit()

    return ResumeUploadResponse(
        user_id=user.id,
        resume_id=resume.id,
        raw_text=body.text,
        skills=skills,
        parsed_sections=ParsedSections(**parsed_sections),
        estimated_years_experience=estimated_years,
    )


@router.get("/list", response_model=ResumeListResponse)
async def list_user_resumes(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all resumes for the authenticated user."""
    # Single query with aggregated skill count (avoids N+1)
    from sqlalchemy.orm import aliased

    skill_count_subq = (
        select(UserSkill.resume_id, func.count(UserSkill.id).label("skill_count"))
        .group_by(UserSkill.resume_id)
        .subquery()
    )

    result = await db.execute(
        select(Resume, func.coalesce(skill_count_subq.c.skill_count, 0))
        .outerjoin(skill_count_subq, Resume.id == skill_count_subq.c.resume_id)
        .where(Resume.user_id == user.id)
        .order_by(Resume.created_at.desc())
    )
    rows = result.all()

    items = [
        ResumeListItem(
            id=r.id,
            filename=r.filename,
            source_type=r.source_type,
            created_at=r.created_at.isoformat(),
            skill_count=count,
        )
        for r, count in rows
    ]

    return ResumeListResponse(resumes=items)


@router.get("/{resume_id}/skills", response_model=SkillsResponse)
async def get_resume_skills(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(404, "Resume not found")
    if resume.user_id != user.id:
        raise HTTPException(403, "Not authorized to access this resume")

    result = await db.execute(
        select(UserSkill, Skill)
        .join(Skill, UserSkill.skill_id == Skill.id)
        .where(UserSkill.resume_id == resume_id)
    )
    rows = result.all()

    skills = []
    categories: dict[str, list[ExtractedSkill]] = {}

    for user_skill, skill in rows:
        extracted = ExtractedSkill(
            name=skill.name,
            category=skill.category or "other",
            confidence=user_skill.confidence or 0.0,
            source=user_skill.source or "unknown",
        )
        skills.append(extracted)

        cat = skill.category or "other"
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(extracted)

    return SkillsResponse(skills=skills, categories=categories)


@router.post("/session", response_model=SessionResponse)
async def create_session(db: AsyncSession = Depends(get_db)):
    user = await _get_or_create_user(db)
    await db.commit()
    return SessionResponse(session_id=user.session_id, user_id=user.id)
