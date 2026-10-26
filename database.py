import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

from backend.app.db.base import Base
# Import every model before using Base.metadata so string-based relationships
# can be resolved regardless of which entry point initializes the database.
from backend.app.models.user import User  # noqa: F401
from backend.app.models.theatre import Theatre  # noqa: F401
from backend.app.models.screens import Screen  # noqa: F401
from backend.app.models.shows import Show  # noqa: F401
from backend.app.models.movies import Movie  # noqa: F401

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in .env")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)