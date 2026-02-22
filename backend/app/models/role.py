from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, LargeBinary, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    title_ph: Mapped[str | None] = mapped_column(String(150), nullable=True)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    salary_range_ph: Mapped[str | None] = mapped_column(String(100), nullable=True)
    salary_range_usd: Mapped[str | None] = mapped_column(String(100), nullable=True)
    salary_min_ph: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max_ph: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seniority: Mapped[str | None] = mapped_column(String(30), nullable=True)
    min_years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    onet_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    embedding: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    demand_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    stability_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    growth_potential: Mapped[float | None] = mapped_column(Float, nullable=True)
    remote_friendly: Mapped[bool | None] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    transitions_from = relationship(
        "CareerTransition",
        foreign_keys="CareerTransition.from_role_id",
        back_populates="from_role",
    )
    transitions_to = relationship(
        "CareerTransition",
        foreign_keys="CareerTransition.to_role_id",
        back_populates="to_role",
    )
