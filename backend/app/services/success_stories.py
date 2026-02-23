"""Template-based success story generator.

Generates relatable 'People Like You' career transition stories based on
the user's current skills, target role, and career category. No external
API calls — all template-driven.
"""

from __future__ import annotations

import json
import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.models.skill import Skill, UserSkill

# Story templates keyed by broad career category.
# Each template has placeholders: {name}, {from_role}, {to_role}, {key_skill},
# {months}, {salary_bump}, {city}.

_NAMES_MALE = [
    "Marco", "Juan", "Miguel", "Rafael", "Carlos", "Paolo",
    "Kenneth", "James", "Mark", "Ariel", "Aldrin", "Jericho",
]
_NAMES_FEMALE = [
    "Maria", "Angela", "Patricia", "Carla", "Jasmine", "Nicole",
    "Kristine", "Denise", "Mae", "Erica", "Rica", "Bea",
]
_CITIES = [
    "Manila", "Cebu City", "Davao City", "Quezon City",
    "Makati", "Taguig", "Clark", "Iloilo City",
]

_STORY_TEMPLATES: dict[str, list[dict]] = {
    "Engineering": [
        {
            "template": (
                "{name} was a junior developer in {city} earning {old_salary}/mo. "
                "After focusing on {key_skill} for {months} months through online courses "
                "and side projects, {name} landed a {to_role} position earning {new_salary}/mo — "
                "a {salary_bump}% increase."
            ),
            "tip": "Building a portfolio of projects that showcase {key_skill} was the game-changer.",
        },
        {
            "template": (
                "Coming from a {from_role} background, {name} felt stuck. "
                "A structured 90-day plan focusing on {key_skill} and contributing to open source "
                "helped {name} transition to {to_role} in {city} with a {salary_bump}% salary jump."
            ),
            "tip": "Open source contributions gave {name} real-world experience that employers valued.",
        },
        {
            "template": (
                "{name} in {city} switched from {from_role} to {to_role} in just {months} months. "
                "The secret? Combining existing problem-solving skills with {key_skill} through "
                "bootcamps and pair programming sessions."
            ),
            "tip": "Pair programming with experienced devs accelerated learning faster than solo study.",
        },
    ],
    "Data": [
        {
            "template": (
                "{name} transitioned from {from_role} to {to_role} in {city}. "
                "By mastering {key_skill} and building data-driven dashboards, "
                "{name} went from {old_salary}/mo to {new_salary}/mo in {months} months."
            ),
            "tip": "Start with real datasets from Kaggle — employers love seeing practical data work.",
        },
        {
            "template": (
                "After {months} months of dedicated study in {key_skill}, "
                "{name} from {city} moved from {from_role} into {to_role}, "
                "earning {salary_bump}% more. The key was building an end-to-end data project."
            ),
            "tip": "An end-to-end project (collect, clean, analyze, visualize) beats many small exercises.",
        },
    ],
    "Product": [
        {
            "template": (
                "{name} leveraged {from_role} experience to become a {to_role} in {city}. "
                "Learning {key_skill} and running user research helped bridge the gap. "
                "Salary jumped {salary_bump}% within {months} months."
            ),
            "tip": "Understanding the user deeply is the best skill for product roles.",
        },
    ],
    "Design": [
        {
            "template": (
                "From {from_role} to {to_role} in {months} months — {name} in {city} "
                "did it by mastering {key_skill} and building a strong portfolio. "
                "The result: a {salary_bump}% salary increase."
            ),
            "tip": "A polished portfolio with 3-5 case studies matters more than certifications.",
        },
    ],
    "Marketing": [
        {
            "template": (
                "{name} pivoted from {from_role} to {to_role} in {city} by learning "
                "{key_skill} and applying it to real campaigns. In {months} months, "
                "{name} went from {old_salary}/mo to {new_salary}/mo."
            ),
            "tip": "Run a personal project or volunteer campaign to build a track record.",
        },
    ],
    "Finance": [
        {
            "template": (
                "With a background as a {from_role}, {name} in {city} transitioned to "
                "{to_role} after {months} months of studying {key_skill}. "
                "The salary bump was {salary_bump}% — proving finance skills transfer well."
            ),
            "tip": "Financial modeling and Excel mastery open doors across many finance roles.",
        },
    ],
    "default": [
        {
            "template": (
                "{name} in {city} made the leap from {from_role} to {to_role} "
                "in {months} months by focusing on {key_skill}. "
                "This earned a {salary_bump}% salary increase and a career they love."
            ),
            "tip": "Consistency beats intensity — 1 hour daily for {months} months adds up fast.",
        },
        {
            "template": (
                "Starting as a {from_role}, {name} wondered if switching to {to_role} "
                "was realistic. After learning {key_skill} in {city} through self-study, "
                "{name} proved it was — with a {salary_bump}% pay increase."
            ),
            "tip": "Break the transition into 30-day sprints. Each sprint = one new sub-skill.",
        },
    ],
}


class SuccessStoryService:
    async def generate_stories(
        self,
        db: AsyncSession,
        user_id: int,
        target_role_id: int,
        count: int = 3,
    ) -> list[dict]:
        """Generate template-based success stories for a target role.

        Returns a list of dicts: {name, story, tip, category, from_role, to_role}.
        """
        # Get target role
        result = await db.execute(select(Role).where(Role.id == target_role_id))
        target_role = result.scalar_one_or_none()
        if not target_role:
            return []

        # Get user skills for context
        result = await db.execute(
            select(Skill.name)
            .join(UserSkill, UserSkill.skill_id == Skill.id)
            .where(UserSkill.user_id == user_id)
        )
        user_skills = [row[0] for row in result.all()]

        # Determine role skills for the key_skill placeholder
        role_skills: list[str] = []
        if target_role.required_skills:
            role_skills = json.loads(target_role.required_skills)

        # Pick a key skill — prefer one the user doesn't have yet
        user_skills_lower = {s.lower() for s in user_skills}
        missing = [s for s in role_skills if s.lower() not in user_skills_lower]
        key_skill = missing[0] if missing else (role_skills[0] if role_skills else "new technologies")

        # Get from_role — a plausible source role
        from_roles = await self._get_feeder_roles(db, target_role)

        category = target_role.category or "default"
        templates = _STORY_TEMPLATES.get(category, _STORY_TEMPLATES["default"])

        # Also mix in default templates if we need more
        all_templates = list(templates)
        if len(all_templates) < count:
            all_templates += _STORY_TEMPLATES["default"]

        random.shuffle(all_templates)

        stories = []
        used_names: set[str] = set()

        for i in range(min(count, len(all_templates))):
            tpl = all_templates[i]
            name = self._pick_name(used_names)
            used_names.add(name)

            city = random.choice(_CITIES)
            from_role = from_roles[i % len(from_roles)] if from_roles else "entry-level professional"
            months = random.randint(3, 12)
            salary_bump = random.randint(15, 60)

            # Compute plausible salary figures
            old_salary = "PHP 25,000"
            new_salary = "PHP 40,000"
            if target_role.salary_min_ph:
                base = max(15000, target_role.salary_min_ph - random.randint(5000, 20000))
                new_val = target_role.salary_min_ph + random.randint(0, 10000)
                salary_bump = round(((new_val - base) / base) * 100)
                old_salary = f"PHP {base:,}"
                new_salary = f"PHP {new_val:,}"

            story_text = tpl["template"].format(
                name=name,
                from_role=from_role,
                to_role=target_role.title,
                key_skill=key_skill,
                months=months,
                salary_bump=salary_bump,
                city=city,
                old_salary=old_salary,
                new_salary=new_salary,
            )

            tip_text = tpl["tip"].format(
                name=name,
                key_skill=key_skill,
                months=months,
            )

            stories.append({
                "name": name,
                "story": story_text,
                "tip": tip_text,
                "category": category,
                "from_role": from_role,
                "to_role": target_role.title,
            })

        return stories

    async def _get_feeder_roles(self, db: AsyncSession, target_role: Role) -> list[str]:
        """Get plausible 'from' role titles for a target role."""
        from app.models.career_graph import CareerTransition

        result = await db.execute(
            select(Role.title)
            .join(CareerTransition, CareerTransition.from_role_id == Role.id)
            .where(CareerTransition.to_role_id == target_role.id)
            .limit(5)
        )
        titles = [row[0] for row in result.all()]

        if not titles:
            # Fallback: same category, lower seniority
            seniority_order = {"entry": 0, "mid": 1, "senior": 2, "lead": 3}
            current_level = seniority_order.get(target_role.seniority or "mid", 1)
            lower_levels = [k for k, v in seniority_order.items() if v < current_level]
            if lower_levels:
                result = await db.execute(
                    select(Role.title)
                    .where(
                        Role.category == target_role.category,
                        Role.seniority.in_(lower_levels),
                    )
                    .limit(3)
                )
                titles = [row[0] for row in result.all()]

        return titles or ["entry-level professional"]

    def _pick_name(self, used: set[str]) -> str:
        all_names = _NAMES_MALE + _NAMES_FEMALE
        available = [n for n in all_names if n not in used]
        if not available:
            available = all_names
        return random.choice(available)
