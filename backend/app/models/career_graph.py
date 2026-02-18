from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CareerTransition(Base):
    __tablename__ = "career_transitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    to_role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, default=0.5)
    typical_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    required_upskills: Mapped[str | None] = mapped_column(Text, nullable=True)
    market_viability: Mapped[float] = mapped_column(Float, default=0.5)
    transition_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    from_role = relationship("Role", foreign_keys=[from_role_id], back_populates="transitions_from")
    to_role = relationship("Role", foreign_keys=[to_role_id], back_populates="transitions_to")


class UserMatch(Base):
    __tablename__ = "user_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    embedding_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    skill_overlap_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    experience_match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    llm_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    market_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    meta_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class TransitionPath(Base):
    __tablename__ = "transition_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    target_role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    path_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_difficulty: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    skill_gaps: Mapped[str | None] = mapped_column(Text, nullable=True)
    roadmap: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
