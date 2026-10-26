from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from sqlalchemy import text

from . import models  # noqa: F401  (registers tables)
from .database import Base, engine
from .routers import ai, students


@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS auth_sessions"))
        connection.execute(text("DROP TABLE IF EXISTS bootstrap_admin"))
        connection.execute(text("DROP TABLE IF EXISTS users"))
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Students Database CRUD API",
    description="FastAPI + SQLite student records manager (with optional local Ollama Q&A).",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(students.router)
app.include_router(ai.router)


@app.get("/", tags=["Health"])
def root():
    return FileResponse(Path(__file__).parent / "static" / "index.html")
