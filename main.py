from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.db_connection import engine, SessionLocal
# from app.db.seed import seed_roles_permissions
from app.db.seed_modified import seed_roles_and_permissions
from app.models.base import Base

from app.api.exception_handlers import register_exception_handlers

from app.api.v1.routers import v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    #init db
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # seed data
    async with SessionLocal() as session:
        await seed_roles_and_permissions(session)
    yield
    #close_db
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)


app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.include_router(v1_router, prefix="/api/v1")