import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

from backend.app.db.base import Base
from backend.app.models.user import User

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