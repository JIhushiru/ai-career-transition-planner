"""Skill overlap matching service — computes hard-skill match scores."""

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.models.skill import Skill, UserSkill


class MatchingService:
    async def get_user_skill_names(self, db: AsyncSession, user_id: int) -> set[str]:
        """Get all skill names for a user."""
        result = await db.execute(
            select(Skill.name)
            .join(UserSkill, UserSkill.skill_id == Skill.id)
            .where(UserSkill.user_id == user_id)
        )
        return {row[0].lower() for row in result.all()}

    def compute_skill_overlap(
        self, user_skills: set[str], role: Role
    ) -> dict:
        """Compute skill overlap between user skills and a role."""
        required = set()
        preferred = set()

        if role.required_skills:
            required = {s.lower() for s in json.loads(role.required_skills)}
        if role.preferred_skills:
            preferred = {s.lower() for s in json.loads(role.preferred_skills)}

        all_role_skills = required | preferred
        if not all_role_skills:
            return {
                "overlap_score": 0.0,
                "required_match": 0.0,
                "preferred_match": 0.0,
                "matched_skills": [],
                "missing_required": [],
                "missing_preferred": [],
            }

        matched_required = required & user_skills
        matched_preferred = preferred & user_skills
        missing_required = required - user_skills
        missing_preferred = preferred - user_skills

        required_score = len(matched_required) / len(required) if required else 1.0
        preferred_score = len(matched_preferred) / len(preferred) if preferred else 0.0

        # Weighted: required skills count 70%, preferred 30%
        overlap_score = required_score * 0.7 + preferred_score * 0.3

        return {
            "overlap_score": round(overlap_score, 4),
            "required_match": round(required_score, 4),
            "preferred_match": round(preferred_score, 4),
            "matched_skills": sorted(matched_required | matched_preferred),
            "missing_required": sorted(missing_required),
            "missing_preferred": sorted(missing_preferred),
        }

    def compute_experience_match(
        self, user_years: int | None, role: Role
    ) -> float:
        """Score experience fit. Returns 0-1."""
        if not user_years or not role.min_years_experience:
            return 0.5

        min_years = role.min_years_experience

        if user_years >= min_years:
            # Over-qualified penalty (mild)
            over = user_years - min_years
            if over > 10:
                return 0.6
            return 1.0 - (over * 0.02)
        else:
            # Under-qualified penalty
            gap = min_years - user_years
            return max(0.0, 1.0 - (gap * 0.15))

    async def compute_all_overlaps(
        self,
        db: AsyncSession,
        user_id: int,
        roles: list[Role],
        user_years: int | None = None,
    ) -> list[dict]:
        """Compute skill overlap for a user against multiple roles."""
        user_skills = await self.get_user_skill_names(db, user_id)

        results = []
        for role in roles:
            overlap = self.compute_skill_overlap(user_skills, role)
            exp_score = self.compute_experience_match(user_years, role)

            results.append({
                "role_id": role.id,
                "overlap_score": overlap["overlap_score"],
                "required_match": overlap["required_match"],
                "experience_score": round(exp_score, 4),
                "matched_skills": overlap["matched_skills"],
                "missing_required": overlap["missing_required"],
                "missing_preferred": overlap["missing_preferred"],
            })

        return results
