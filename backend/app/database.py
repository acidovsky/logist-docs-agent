"""Подключение к базе данных SQLModel."""

import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")

# SQLite в FastAPI требует отключения проверки потока для синхронных сессий.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
else:
    engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables() -> None:
    """Создать таблицы при первом запуске."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Отдать сессию БД для Depends."""
    with Session(engine) as session:
        yield session
