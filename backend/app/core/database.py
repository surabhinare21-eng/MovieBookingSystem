
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


# Engine: one per application process
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

# Factory for database sessions
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=True,
)


# Base class for all ORM models
class Base(DeclarativeBase):
    pass


# FastAPI dependency
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
