"""Skill overlap matching service — computes hard-skill match scores
with fuzzy matching for aliases and near-matches."""

import json
from difflib import SequenceMatcher

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.models.skill import Skill, UserSkill

# Common aliases that should match each other
SKILL_ALIASES: dict[str, set[str]] = {
    "react": {"react", "react.js", "reactjs"},
    "vue": {"vue", "vue.js", "vuejs"},
    "next": {"next", "next.js", "nextjs"},
    "node": {"node", "node.js", "nodejs"},
    "express": {"express", "express.js", "expressjs"},
    "angular": {"angular", "angularjs"},
    "typescript": {"typescript", "ts"},
    "javascript": {"javascript", "js"},
    "python": {"python", "py"},
    "c++": {"c++", "cpp"},
    "c#": {"c#", "c sharp", "csharp"},
    ".net": {".net", "dotnet", "asp.net"},
    "kubernetes": {"kubernetes", "k8s"},
    "terraform": {"terraform", "tf"},
    "postgresql": {"postgresql", "postgres"},
    "mongodb": {"mongodb", "mongo"},
    "machine learning": {"machine learning", "ml"},
    "natural language processing": {"natural language processing", "nlp"},
    "devops": {"devops", "dev ops"},
    "ci/cd": {"ci/cd", "ci cd", "cicd"},
    "rest api": {"rest api", "rest apis", "restful api", "restful apis"},
    "power bi": {"power bi", "powerbi"},
    "spring boot": {"spring boot", "springboot"},
    "quality assurance": {"quality assurance", "qa"},
    "user experience": {"user experience", "ux"},
    "user interface": {"user interface", "ui"},
    "ui/ux": {"ui/ux", "ux/ui", "ui/ux design", "ux/ui design"},
    "a/b testing": {"a/b testing", "ab testing", "split testing"},
    "scikit-learn": {"scikit-learn", "sklearn", "scikit learn"},
    "amazon web services": {"amazon web services", "aws"},
    "google cloud": {"google cloud", "google cloud platform", "gcp"},
    "microsoft azure": {"microsoft azure", "azure"},
    "pytorch": {"pytorch", "py torch"},
    "data structures & algorithms": {
        "data structures & algorithms",
        "data structures and algorithms",
        "dsa",
    },
    "project management": {"project management", "pm"},
    "agile": {"agile", "agile methodologies", "agile methodology"},
    "scrum": {"scrum", "scrum master"},
    "six sigma": {"six sigma", "lean six sigma"},
    "excel": {"excel", "microsoft excel", "ms excel"},
    "photoshop": {"photoshop", "adobe photoshop"},
    "illustrator": {"illustrator", "adobe illustrator"},
}

# Build reverse lookup: lowercase alias -> canonical group key
_ALIAS_LOOKUP: dict[str, str] = {}
for _canonical, _aliases in SKILL_ALIASES.items():
    for _alias in _aliases:
        _ALIAS_LOOKUP[_alias.lower()] = _canonical


def _normalize_skill(skill: str) -> str:
    """Normalize a skill name to its canonical form."""
    lower = skill.lower().strip()
    return _ALIAS_LOOKUP.get(lower, lower)


def _fuzzy_match(user_skill: str, role_skill: str, threshold: float = 0.85) -> bool:
    """Check if two skills are close enough to be considered a match."""
    a = user_skill.lower().strip()
    b = role_skill.lower().strip()

    if a == b:
        return True

    if _normalize_skill(a) == _normalize_skill(b):
        return True

    # Substring containment — only when the shorter is >70% of the longer
    if len(a) > 3 and len(b) > 3:
        if a in b or b in a:
            shorter, longer = (a, b) if len(a) < len(b) else (b, a)
            if len(shorter) / len(longer) > 0.7:
                return True

    ratio = SequenceMatcher(None, a, b).ratio()
    return ratio >= threshold


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
        """Compute skill overlap between user skills and a role using fuzzy matching."""
        required: set[str] = set()
        preferred: set[str] = set()

        if role.required_skills:
            required = set(json.loads(role.required_skills))
        if role.preferred_skills:
            preferred = set(json.loads(role.preferred_skills))

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

        user_normalized = {_normalize_skill(s) for s in user_skills}

        def is_matched(role_skill: str) -> bool:
            role_lower = role_skill.lower()
            if role_lower in user_skills:
                return True
            if _normalize_skill(role_lower) in user_normalized:
                return True
            for us in user_skills:
                if _fuzzy_match(us, role_lower):
                    return True
            return False

        matched_required = {s for s in required if is_matched(s)}
        matched_preferred = {s for s in preferred if is_matched(s)}
        missing_required = required - matched_required
        missing_preferred = preferred - matched_preferred

        required_score = len(matched_required) / len(required) if required else 1.0
        preferred_score = len(matched_preferred) / len(preferred) if preferred else 0.0

        # Adjust weighting: if only one skill list exists, score on that alone
        if required and not preferred:
            overlap_score = required_score
        elif preferred and not required:
            overlap_score = preferred_score
        else:
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
            over = user_years - min_years
            if over > 10:
                return 0.6
            return 1.0 - (over * 0.02)
        else:
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
