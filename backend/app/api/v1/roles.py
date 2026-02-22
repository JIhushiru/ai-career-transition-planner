import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.role import Role
from app.models.career_graph import CareerTransition
from app.schemas.role import RoleResponse, RoleListResponse, TransitionResponse

router = APIRouter(prefix="/roles", tags=["roles"])


def _role_to_response(role: Role) -> RoleResponse:
    return RoleResponse(
        id=role.id,
        title=role.title,
        title_ph=role.title_ph,
        category=role.category,
        description=role.description,
        required_skills=json.loads(role.required_skills) if role.required_skills else [],
        preferred_skills=json.loads(role.preferred_skills) if role.preferred_skills else [],
        salary_range_ph=role.salary_range_ph,
        salary_range_usd=role.salary_range_usd,
        salary_min_ph=role.salary_min_ph,
        salary_max_ph=role.salary_max_ph,
        seniority=role.seniority,
        min_years_experience=role.min_years_experience,
        demand_score=role.demand_score,
        stability_score=role.stability_score,
        growth_potential=role.growth_potential,
        remote_friendly=role.remote_friendly,
    )


@router.get("", response_model=RoleListResponse)
async def list_roles(
    category: str | None = Query(None),
    seniority: str | None = Query(None),
    search: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    query = select(Role)
    count_query = select(sa_func.count(Role.id))

    if category:
        query = query.where(Role.category == category)
        count_query = count_query.where(Role.category == category)
    if seniority:
        query = query.where(Role.seniority == seniority)
        count_query = count_query.where(Role.seniority == seniority)
    if search:
        pattern = f"%{search}%"
        query = query.where(Role.title.ilike(pattern) | Role.description.ilike(pattern))
        count_query = count_query.where(
            Role.title.ilike(pattern) | Role.description.ilike(pattern)
        )

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Role.category, Role.title).offset(skip).limit(limit)
    result = await db.execute(query)
    roles = result.scalars().all()

    return RoleListResponse(
        roles=[_role_to_response(r) for r in roles],
        total=total,
    )


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(role_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(404, "Role not found")
    return _role_to_response(role)


@router.get("/{role_id}/transitions", response_model=list[TransitionResponse])
async def get_role_transitions(role_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(404, "Role not found")

    result = await db.execute(
        select(CareerTransition, Role)
        .join(Role, CareerTransition.to_role_id == Role.id)
        .where(CareerTransition.from_role_id == role_id)
        .order_by(CareerTransition.difficulty)
    )
    rows = result.all()

    transitions = []
    for ct, to_role in rows:
        transitions.append(
            TransitionResponse(
                id=ct.id,
                from_role=_role_to_response(role),
                to_role=_role_to_response(to_role),
                difficulty=ct.difficulty,
                typical_months=ct.typical_months,
                required_upskills=(
                    json.loads(ct.required_upskills) if ct.required_upskills else []
                ),
                market_viability=ct.market_viability,
                transition_type=ct.transition_type,
            )
        )
    return transitions


@router.get("/categories/list")
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Role.category, sa_func.count(Role.id))
        .group_by(Role.category)
        .order_by(Role.category)
    )
    return [{"category": cat, "count": count} for cat, count in result.all()]
