from fastapi import FastAPI

from backend.app.routers.auth import router as auth_router

app = FastAPI(title="Movie Ticket Booking System")

app.include_router(auth_router)

@app.get("/")
def root():
    return{
        "message":"Movie Ticket Booking System Api is running"
    }