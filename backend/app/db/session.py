# backend/app/db/session.py
from sqlalchemy.orm import sessionmaker
from database import engine

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()