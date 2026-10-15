from contextlib import asynccontextmanager
from fastapi import FastAPI

from app import models
import app.models
from app.database import Base, engine, AsyncSessionLocal
from app.seed import seed_categories
from app.routers import emails, health, categories, stats
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await seed_categories(session)
    yield
    await engine.dispose()

app = FastAPI(title="Email Parser API", lifespan=lifespan)
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(emails.router, prefix="/api/emails", tags=["emails"])

