from fastapi import FastAPI
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

app.include_router(auth_router)

@app.get("/")
def root():
    return{
        "message":"Movie Ticket Booking System Api is running"
    }