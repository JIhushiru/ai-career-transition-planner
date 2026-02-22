from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.resume import router as resume_router
from app.api.v1.roles import router as roles_router
from app.api.v1.career import router as career_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(health_router)
api_router.include_router(resume_router)
api_router.include_router(roles_router)
api_router.include_router(career_router)
