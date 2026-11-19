"""Точка входа FastAPI-приложения."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from .database import engine, create_db_and_tables
from . import models  # noqa: F401 — регистрация моделей в метаданных


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создать таблицы при старте и корректно закрыть ресурсы."""
    create_db_and_tables()
    yield


app = FastAPI(
    title="Logist Docs Agent API",
    version="2.0.0",
    lifespan=lifespan,
)

# Frontend будет жить на localhost:5173.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    """Проверка, что backend жив."""
    return {"status": "ok"}
