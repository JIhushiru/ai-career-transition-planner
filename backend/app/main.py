from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, AsyncSessionLocal
from app.api.v1.router import api_router
from app.data.seed import run_seed
from app.services.embedding_service import EmbeddingService


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await run_seed()
    async with AsyncSessionLocal() as db:
        count = await EmbeddingService().compute_role_embeddings(db)
        print(f"Computed embeddings for {count} roles")
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
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
