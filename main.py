from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from backend.app.db.base import Base
from backend.app.models.user import User        # noqa: F401
from backend.app.models.theatre import Theatre  # noqa: F401
from backend.app.routers.auth import router as auth_router
from backend.app.routers.root_admin import router as root_admin_router
from backend.app.routers.theatre_admin import router as theatre_admin_router
from backend.app.routers.show import router as show_router
from backend.app.models.shows import Show  
from backend.app.models.screens import Screen  # noqa: F401
from backend.app.models.movies import Movie    # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Importing the models above registers them with Base.metadata.
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
app.include_router(root_admin_router)
app.include_router(theatre_admin_router)
app.include_router(show_router)


@app.get("/")
def root():
    return {
        "message": "Movie Ticket Booking System Api is running"
    }