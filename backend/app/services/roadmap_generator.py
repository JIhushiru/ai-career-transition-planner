"""Skill gap analysis and learning roadmap generator."""

import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.models.skill import Skill, UserSkill
from app.ai.provider_factory import ProviderFactory

logger = logging.getLogger(__name__)

HOURS_BY_PRIORITY = {"high": 80, "medium": 40, "low": 20}


class RoadmapGenerator:
    async def analyze_skill_gaps(
        self,
        db: AsyncSession,
        user_id: int,
        target_role_id: int,
    ) -> dict:
        """Analyze skill gaps between a user and a target role."""
        # Get user skills
        result = await db.execute(
            select(Skill.name)
            .join(UserSkill, UserSkill.skill_id == Skill.id)
            .where(UserSkill.user_id == user_id)
        )
        user_skills = {row[0].lower() for row in result.all()}

        # Get target role
        result = await db.execute(select(Role).where(Role.id == target_role_id))
        role = result.scalar_one_or_none()
        if not role:
            return {"error": "Role not found"}

        required = set()
        preferred = set()
        if role.required_skills:
            required = {s for s in json.loads(role.required_skills)}
        if role.preferred_skills:
            preferred = {s for s in json.loads(role.preferred_skills)}

        # Identify gaps
        missing_required = [s for s in required if s.lower() not in user_skills]
        missing_preferred = [s for s in preferred if s.lower() not in user_skills]
        existing_match = [
            s for s in (required | preferred) if s.lower() in user_skills
        ]

        # Prioritize gaps
        gaps = []
        for skill in missing_required:
            gaps.append({
                "skill": skill,
                "priority": "high",
                "estimated_hours": HOURS_BY_PRIORITY["high"],
                "resources": [],
            })
        for skill in missing_preferred:
            gaps.append({
                "skill": skill,
                "priority": "medium",
                "estimated_hours": HOURS_BY_PRIORITY["medium"],
                "resources": [],
            })

        total_hours = sum(g["estimated_hours"] for g in gaps)

        # Generate milestones
        milestones = self._generate_milestones(gaps)

        return {
            "role": role,
            "existing_skills": existing_match,
            "skill_gaps": gaps,
            "total_estimated_hours": total_hours,
            "milestones": milestones,
        }

    def _generate_milestones(self, gaps: list[dict]) -> list[dict]:
        """Create timeline milestones from skill gaps."""
        milestones = []
        cumulative_hours = 0

        high_gaps = [g for g in gaps if g["priority"] == "high"]
        medium_gaps = [g for g in gaps if g["priority"] == "medium"]

        if high_gaps:
            hours = sum(g["estimated_hours"] for g in high_gaps)
            cumulative_hours += hours
            milestones.append({
                "phase": 1,
                "title": "Core Skills Foundation",
                "description": f"Learn {len(high_gaps)} critical required skills",
                "skills": [g["skill"] for g in high_gaps],
                "estimated_hours": hours,
                "estimated_weeks": max(1, hours // 10),
            })

        if medium_gaps:
            hours = sum(g["estimated_hours"] for g in medium_gaps)
            cumulative_hours += hours
            milestones.append({
                "phase": 2,
                "title": "Expand Skill Set",
                "description": f"Learn {len(medium_gaps)} preferred skills",
                "skills": [g["skill"] for g in medium_gaps],
                "estimated_hours": hours,
                "estimated_weeks": max(1, hours // 10),
            })

        if gaps:
            milestones.append({
                "phase": len(milestones) + 1,
                "title": "Portfolio & Practice",
                "description": "Build projects demonstrating new skills",
                "skills": [],
                "estimated_hours": 40,
                "estimated_weeks": 4,
            })

        return milestones

    async def enrich_with_resources(self, gaps: list[dict]) -> list[dict]:
        """Use Gemini with search grounding to find learning resources."""
        try:
            provider = ProviderFactory.get_provider("search")
        except RuntimeError:
            logger.warning("No AI provider for resource search")
            return gaps

        from app.ai.gemini_provider import GeminiProvider

        if not isinstance(provider, GeminiProvider):
            return gaps

        for gap in gaps[:10]:  # Limit to avoid rate limits
            try:
                result = await provider.generate_with_search(
                    f"Find the top 3 free online courses or resources to learn "
                    f"'{gap['skill']}' for a career in technology/business. "
                    f"List course name, platform, and URL.",
                    system_prompt="Return concise learning resource recommendations.",
                )
                resources = []
                if result.get("sources"):
                    for source in result["sources"][:3]:
                        title = source.get("title", "Resource")
                        uri = source.get("uri", "")
                        resources.append({"title": title, "url": uri})
                if not resources and result.get("text"):
                    resources = [{"title": result["text"][:150], "url": ""}]
                gap["resources"] = resources
            except Exception as e:
                logger.warning(f"Resource search failed for {gap['skill']}: {e}")

        return gaps
