import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, AsyncSessionLocal
from app.api.v1.router import api_router
from app.data.seed import run_seed
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        await run_seed()
        async with AsyncSessionLocal() as db:
            count = await EmbeddingService().compute_role_embeddings(db)
            logger.info("Computed embeddings for %d roles", count)
    except Exception:
        logger.exception("Startup initialization failed — app will start but some features may be unavailable")
    yield


app = FastAPI(
    title="AI Career Transition Planner",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_router, prefix="/api/v1")
