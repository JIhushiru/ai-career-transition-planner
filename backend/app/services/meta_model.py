"""Meta-Model hybrid scorer — combines multiple AI signal layers."""

import json
import logging

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career_graph import UserMatch
from app.models.resume import Resume
from app.models.role import Role
from app.models.skill import UserSkill, Skill
from app.services.embedding_service import EmbeddingService
from app.services.matching_service import MatchingService
from app.ai.provider_factory import ProviderFactory

logger = logging.getLogger(__name__)


# Weight presets per career mode
WEIGHT_PRESETS: dict[str, dict[str, float]] = {
    "growth": {
        "embedding": 0.30,
        "skill_overlap": 0.25,
        "experience": 0.15,
        "llm": 0.20,
        "market": 0.10,
    },
    "stability": {
        "embedding": 0.20,
        "skill_overlap": 0.30,
        "experience": 0.20,
        "llm": 0.10,
        "market": 0.20,
    },
    "pivot": {
        "embedding": 0.35,
        "skill_overlap": 0.15,
        "experience": 0.10,
        "llm": 0.25,
        "market": 0.15,
    },
    "late_career": {
        "embedding": 0.20,
        "skill_overlap": 0.30,
        "experience": 0.25,
        "llm": 0.05,
        "market": 0.20,
    },
}


class MetaModelScorer:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.matching_service = MatchingService()

    async def score_matches(
        self,
        db: AsyncSession,
        user_id: int,
        resume_text: str,
        user_years: int | None = None,
        career_mode: str = "growth",
        top_k: int = 15,
        use_llm: bool = True,
    ) -> list[dict]:
        """Run the full meta-model scoring pipeline.

        Pipeline:
        1. Compute user embedding from resume
        2. Match against role embeddings (cosine similarity)
        3. Compute skill overlap scores
        4. Compute experience match
        5. (Optional) LLM assessment for top candidates
        6. Combine with weighted meta-score
        """
        weights = WEIGHT_PRESETS.get(career_mode, WEIGHT_PRESETS["growth"])

        # Get user skills
        result = await db.execute(
            select(Skill.name)
            .join(UserSkill, UserSkill.skill_id == Skill.id)
            .where(UserSkill.user_id == user_id)
        )
        user_skill_names = [row[0] for row in result.all()]

        # Step 1: Embedding similarity
        user_embedding = self.embedding_service.build_user_embedding(
            resume_text, user_skill_names
        )
        embedding_matches = await self.embedding_service.match_user_to_roles(
            db, user_embedding, top_k=top_k * 2
        )
        embedding_scores = {role_id: score for role_id, score in embedding_matches}

        # Get candidate roles
        candidate_ids = [role_id for role_id, _ in embedding_matches[:top_k * 2]]
        result = await db.execute(select(Role).where(Role.id.in_(candidate_ids)))
        roles = result.scalars().all()
        role_map = {r.id: r for r in roles}

        # Step 2: Skill overlap
        overlaps = await self.matching_service.compute_all_overlaps(
            db, user_id, roles, user_years
        )
        overlap_map = {o["role_id"]: o for o in overlaps}

        # Step 3: Compute meta-scores
        scored_candidates = []
        for role_id in candidate_ids:
            role = role_map.get(role_id)
            if not role:
                continue

            emb_score = embedding_scores.get(role_id, 0.0)
            overlap = overlap_map.get(role_id, {})
            skill_score = overlap.get("overlap_score", 0.0)
            exp_score = overlap.get("experience_score", 0.5)
            market_score = role.demand_score or 0.5

            # Late-career filter: penalize entry-level roles
            if career_mode == "late_career" and role.seniority == "entry":
                exp_score *= 0.3

            # Stability mode: boost stable roles
            if career_mode == "stability" and role.stability_score:
                market_score = (market_score + role.stability_score) / 2

            meta_score = (
                weights["embedding"] * emb_score
                + weights["skill_overlap"] * skill_score
                + weights["experience"] * exp_score
                + weights["llm"] * 0.5  # placeholder until LLM scoring
                + weights["market"] * market_score
            )

            scored_candidates.append({
                "role_id": role_id,
                "role": role,
                "meta_score": round(meta_score, 4),
                "breakdown": {
                    "embedding_score": round(emb_score, 4),
                    "skill_overlap_score": round(skill_score, 4),
                    "experience_match_score": round(exp_score, 4),
                    "llm_score": None,
                    "market_score": round(market_score, 4),
                },
                "missing_required": overlap.get("missing_required", []),
                "matched_skills": overlap.get("matched_skills", []),
                "explanation": None,
            })

        # Sort by meta_score
        scored_candidates.sort(key=lambda x: x["meta_score"], reverse=True)
        top_candidates = scored_candidates[:top_k]

        # Step 4: Optional LLM scoring for top 5
        if use_llm and top_candidates:
            top_candidates = await self._llm_enrich(
                top_candidates[:5],
                user_skill_names,
                resume_text,
                career_mode,
                weights,
            ) + top_candidates[5:]

        # Save matches to DB
        for candidate in top_candidates:
            match = UserMatch(
                user_id=user_id,
                role_id=candidate["role_id"],
                embedding_score=candidate["breakdown"]["embedding_score"],
                skill_overlap_score=candidate["breakdown"]["skill_overlap_score"],
                experience_match_score=candidate["breakdown"]["experience_match_score"],
                llm_score=candidate["breakdown"].get("llm_score"),
                market_score=candidate["breakdown"]["market_score"],
                meta_score=candidate["meta_score"],
                explanation=candidate.get("explanation"),
            )
            db.add(match)

        await db.commit()
        return top_candidates

    async def _llm_enrich(
        self,
        candidates: list[dict],
        user_skills: list[str],
        resume_text: str,
        career_mode: str,
        weights: dict[str, float],
    ) -> list[dict]:
        """Use LLM to score and explain top candidates."""
        try:
            provider = ProviderFactory.get_provider("reasoning")
        except RuntimeError:
            logger.warning("No AI provider available for LLM enrichment")
            return candidates

        resume_summary = " ".join(resume_text.split()[:200])

        for candidate in candidates:
            role = candidate["role"]
            prompt = (
                f"Career matching assessment:\n\n"
                f"Candidate skills: {', '.join(user_skills[:20])}\n"
                f"Resume excerpt: {resume_summary}\n"
                f"Career mode: {career_mode}\n\n"
                f"Target role: {role.title}\n"
                f"Role description: {role.description or 'N/A'}\n"
                f"Required skills: {role.required_skills or '[]'}\n"
                f"Seniority: {role.seniority or 'N/A'}\n\n"
                f"Rate this match 0.0-1.0 and explain in 2-3 sentences.\n"
                f"Respond as JSON: {{\"score\": 0.X, \"explanation\": \"...\"}}"
            )

            try:
                result = await provider.generate_structured(
                    prompt,
                    schema={"score": "float", "explanation": "string"},
                    system_prompt="You are a career advisor AI. Rate job matches accurately.",
                )
                llm_score = min(max(float(result.get("score", 0.5)), 0.0), 1.0)
                explanation = result.get("explanation", "")

                candidate["breakdown"]["llm_score"] = round(llm_score, 4)
                candidate["explanation"] = explanation

                # Recompute meta_score with actual LLM score
                b = candidate["breakdown"]
                candidate["meta_score"] = round(
                    weights["embedding"] * (b["embedding_score"] or 0)
                    + weights["skill_overlap"] * (b["skill_overlap_score"] or 0)
                    + weights["experience"] * (b["experience_match_score"] or 0)
                    + weights["llm"] * llm_score
                    + weights["market"] * (b["market_score"] or 0),
                    4,
                )
            except Exception as e:
                logger.warning(f"LLM scoring failed for {role.title}: {e}")

        candidates.sort(key=lambda x: x["meta_score"], reverse=True)
        return candidates
