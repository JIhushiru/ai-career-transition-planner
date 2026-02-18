"""Seed the database with roles and career transitions from JSON data files."""

import asyncio
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, init_db
from app.models.role import Role
from app.models.career_graph import CareerTransition

DATA_DIR = Path(__file__).parent


async def seed_roles(db: AsyncSession) -> dict[str, int]:
    """Seed roles from roles_ph.json. Returns mapping of title -> id."""
    roles_path = DATA_DIR / "roles_ph.json"
    if not roles_path.exists():
        print("roles_ph.json not found, skipping role seeding")
        return {}

    with open(roles_path) as f:
        raw = json.load(f)

    # Support both {"roles": [...]} and plain [...] formats
    roles_data = raw.get("roles", raw) if isinstance(raw, dict) else raw

    title_to_id: dict[str, int] = {}

    for entry in roles_data:
        result = await db.execute(select(Role).where(Role.title == entry["title"]))
        existing = result.scalar_one_or_none()
        if existing:
            title_to_id[entry["title"]] = existing.id
            continue

        role = Role(
            title=entry["title"],
            title_ph=entry.get("title_ph"),
            category=entry.get("category"),
            description=entry.get("description"),
            required_skills=json.dumps(entry.get("required_skills", [])),
            preferred_skills=json.dumps(entry.get("preferred_skills", [])),
            salary_range_ph=entry.get("salary_range_ph"),
            salary_range_usd=entry.get("salary_range_usd"),
            seniority=entry.get("seniority"),
            min_years_experience=entry.get("min_years_experience"),
            onet_code=entry.get("onet_code"),
            demand_score=entry.get("demand_score"),
            stability_score=entry.get("stability_score"),
            growth_potential=entry.get("growth_potential"),
            remote_friendly=entry.get("remote_friendly", False),
        )
        db.add(role)
        await db.flush()
        title_to_id[entry["title"]] = role.id

    await db.commit()
    print(f"Seeded {len(title_to_id)} roles")
    return title_to_id


async def seed_transitions(db: AsyncSession, title_to_id: dict[str, int]) -> int:
    """Seed career transitions from transitions.json."""
    transitions_path = DATA_DIR / "transitions.json"
    if not transitions_path.exists():
        print("transitions.json not found, skipping transition seeding")
        return 0

    with open(transitions_path) as f:
        transitions_data = json.load(f)

    count = 0
    for entry in transitions_data:
        from_title = entry["from_role"]
        to_title = entry["to_role"]

        from_id = title_to_id.get(from_title)
        to_id = title_to_id.get(to_title)

        if not from_id or not to_id:
            continue

        result = await db.execute(
            select(CareerTransition).where(
                CareerTransition.from_role_id == from_id,
                CareerTransition.to_role_id == to_id,
            )
        )
        if result.scalar_one_or_none():
            continue

        transition = CareerTransition(
            from_role_id=from_id,
            to_role_id=to_id,
            difficulty=entry.get("difficulty", 0.5),
            typical_months=entry.get("typical_months"),
            required_upskills=json.dumps(entry.get("required_upskills", [])),
            market_viability=entry.get("market_viability", 0.5),
            transition_type=entry.get("transition_type"),
        )
        db.add(transition)
        count += 1

    await db.commit()
    print(f"Seeded {count} transitions")
    return count


async def run_seed():
    """Run all seed operations."""
    await init_db()
    async with AsyncSessionLocal() as db:
        title_to_id = await seed_roles(db)
        await seed_transitions(db, title_to_id)
    print("Seeding complete!")


if __name__ == "__main__":
    asyncio.run(run_seed())
