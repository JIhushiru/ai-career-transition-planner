"""Embedding service using sentence-transformers for semantic similarity."""

import json
import struct
from functools import lru_cache

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.role import Role


def _get_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embedding_model)


@lru_cache(maxsize=1)
def get_embedding_model():
    return _get_model()


def encode_text(text: str) -> np.ndarray:
    model = get_embedding_model()
    return model.encode(text, normalize_embeddings=True)


def encode_texts(texts: list[str]) -> np.ndarray:
    model = get_embedding_model()
    return model.encode(texts, normalize_embeddings=True, batch_size=32)


def embedding_to_bytes(embedding: np.ndarray) -> bytes:
    return struct.pack(f"{len(embedding)}f", *embedding.astype(np.float32))


def bytes_to_embedding(data: bytes) -> np.ndarray:
    count = len(data) // 4
    return np.array(struct.unpack(f"{count}f", data), dtype=np.float32)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    if a.ndim == 1:
        a = a.reshape(1, -1)
    if b.ndim == 1:
        b = b.reshape(1, -1)
    sim = np.dot(a, b.T)
    return float(sim[0][0])


def cosine_similarity_batch(query: np.ndarray, corpus: np.ndarray) -> np.ndarray:
    if query.ndim == 1:
        query = query.reshape(1, -1)
    return np.dot(corpus, query.T).flatten()


class EmbeddingService:
    def build_user_embedding(self, resume_text: str, skills: list[str]) -> np.ndarray:
        """Create a combined embedding from resume text and extracted skills."""
        skills_text = ", ".join(skills) if skills else ""
        combined = f"{resume_text}\n\nKey Skills: {skills_text}"
        # Truncate to ~500 words to stay within model limits
        words = combined.split()
        if len(words) > 500:
            combined = " ".join(words[:500])
        return encode_text(combined)

    def build_role_embedding(self, role: Role) -> np.ndarray:
        """Create embedding for a role from its description and skills."""
        parts = [role.title]
        if role.description:
            parts.append(role.description)
        if role.required_skills:
            skills = json.loads(role.required_skills)
            parts.append("Required skills: " + ", ".join(skills))
        if role.preferred_skills:
            skills = json.loads(role.preferred_skills)
            parts.append("Preferred skills: " + ", ".join(skills))
        text = ". ".join(parts)
        return encode_text(text)

    async def compute_role_embeddings(self, db: AsyncSession) -> int:
        """Pre-compute and store embeddings for all roles."""
        result = await db.execute(select(Role))
        roles = result.scalars().all()

        texts = []
        for role in roles:
            parts = [role.title]
            if role.description:
                parts.append(role.description)
            if role.required_skills:
                skills = json.loads(role.required_skills)
                parts.append("Required skills: " + ", ".join(skills))
            texts.append(". ".join(parts))

        embeddings = encode_texts(texts)

        for role, emb in zip(roles, embeddings):
            role.embedding = embedding_to_bytes(emb)

        await db.commit()
        return len(roles)

    async def match_user_to_roles(
        self,
        db: AsyncSession,
        user_embedding: np.ndarray,
        top_k: int = 20,
    ) -> list[tuple[int, float]]:
        """Match user embedding against all role embeddings.
        Returns list of (role_id, similarity_score) sorted by score desc.
        """
        result = await db.execute(select(Role).where(Role.embedding.isnot(None)))
        roles = result.scalars().all()

        if not roles:
            return []

        role_ids = [r.id for r in roles]
        role_embeddings = np.array([bytes_to_embedding(r.embedding) for r in roles])

        similarities = cosine_similarity_batch(user_embedding, role_embeddings)

        indexed = list(zip(role_ids, similarities.tolist()))
        indexed.sort(key=lambda x: x[1], reverse=True)

        return indexed[:top_k]
