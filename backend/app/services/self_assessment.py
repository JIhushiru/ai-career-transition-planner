"""Skill self-assessment service — allows users to manually rate their
skills and merges them with resume-extracted skills."""

import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.models.skill import Skill, UserSkill

logger = logging.getLogger(__name__)


class SelfAssessmentService:
    async def get_assessment_questions(
        self, db: AsyncSession, target_role_id: int | None = None
    ) -> list[dict]:
        """Generate skill assessment questions based on a target role or
        common skills across all roles."""

        if target_role_id:
            result = await db.execute(
                select(Role).where(Role.id == target_role_id)
            )
            role = result.scalar_one_or_none()
            if role:
                return self._build_role_questions(role)

        # Generic assessment across top skills
        return self._build_generic_questions()

    def _build_role_questions(self, role: Role) -> list[dict]:
        """Build assessment questions for a specific target role."""
        questions = []

        required = json.loads(role.required_skills) if role.required_skills else []
        preferred = json.loads(role.preferred_skills) if role.preferred_skills else []

        for skill in required:
            questions.append({
                "skill": skill,
                "importance": "required",
                "question": f"How would you rate your proficiency in {skill}?",
                "scale": {
                    "0": "No experience",
                    "1": "Beginner — Aware of it, basic understanding",
                    "2": "Intermediate — Used it in projects or work",
                    "3": "Advanced — Significant experience, can teach others",
                    "4": "Expert — Deep expertise, industry-level mastery",
                },
            })

        for skill in preferred:
            questions.append({
                "skill": skill,
                "importance": "preferred",
                "question": f"How would you rate your proficiency in {skill}?",
                "scale": {
                    "0": "No experience",
                    "1": "Beginner — Aware of it, basic understanding",
                    "2": "Intermediate — Used it in projects or work",
                    "3": "Advanced — Significant experience, can teach others",
                    "4": "Expert — Deep expertise, industry-level mastery",
                },
            })

        return questions

    def _build_generic_questions(self) -> list[dict]:
        """Build a generic skills assessment covering common categories."""
        common_skills = [
            # Technical
            ("Python", "technical"),
            ("JavaScript", "technical"),
            ("SQL", "technical"),
            ("HTML/CSS", "technical"),
            # Tools
            ("Git", "tool"),
            ("Excel", "tool"),
            ("AWS/Azure/GCP", "tool"),
            ("Docker", "tool"),
            # Domain
            ("Data Analysis", "domain"),
            ("Machine Learning", "domain"),
            ("Agile/Scrum", "domain"),
            ("DevOps", "domain"),
            # Soft
            ("Leadership", "soft"),
            ("Communication", "soft"),
            ("Project Management", "soft"),
            ("Problem Solving", "soft"),
        ]

        questions = []
        for skill, category in common_skills:
            questions.append({
                "skill": skill,
                "category": category,
                "importance": "general",
                "question": f"How would you rate your proficiency in {skill}?",
                "scale": {
                    "0": "No experience",
                    "1": "Beginner",
                    "2": "Intermediate",
                    "3": "Advanced",
                    "4": "Expert",
                },
            })
        return questions

    async def save_assessment(
        self,
        db: AsyncSession,
        user_id: int,
        ratings: list[dict],
    ) -> dict:
        """Save self-assessment ratings as user skills.

        ratings: [{"skill": "Python", "rating": 3}, ...]
        """
        added = 0
        updated = 0

        for rating in ratings:
            skill_name = rating.get("skill", "").strip()
            level = rating.get("rating", 0)

            if not skill_name or level <= 0:
                continue

            # Map rating to numeric proficiency (0.0–1.0)
            proficiency = {1: 0.25, 2: 0.5, 3: 0.75, 4: 1.0}.get(level, 0.25)
            # Map rating to confidence score
            confidence = min(0.5 + (level * 0.1), 0.95)

            # Find or create the skill
            result = await db.execute(
                select(Skill).where(Skill.name == skill_name)
            )
            skill = result.scalar_one_or_none()

            if not skill:
                skill = Skill(name=skill_name, category=rating.get("category", "technical"))
                db.add(skill)
                await db.flush()

            # Check if user already has a self-assessment entry for this skill
            # (filter by resume_id IS NULL to avoid colliding with resume-extracted records)
            result = await db.execute(
                select(UserSkill).where(
                    UserSkill.user_id == user_id,
                    UserSkill.skill_id == skill.id,
                    UserSkill.resume_id.is_(None),
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.proficiency = proficiency
                existing.confidence = confidence
                existing.source = "self_assessment"
                updated += 1
            else:
                user_skill = UserSkill(
                    user_id=user_id,
                    skill_id=skill.id,
                    proficiency=proficiency,
                    confidence=confidence,
                    source="self_assessment",
                )
                db.add(user_skill)
                added += 1

        await db.commit()

        return {
            "added": added,
            "updated": updated,
            "total": added + updated,
        }
