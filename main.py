from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import engine
from backend.app.routers.auth import router as auth_router
from backend.app.db.base import Base
from backend.app.models.user import User



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Importing User registers it with Base.metadata.
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

    yield
app = FastAPI(
    title="Movie Ticket Booking System",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/")
def root():
    return{
        "message":"Movie Ticket Booking System Api is running"
    }