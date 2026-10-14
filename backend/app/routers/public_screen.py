from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.screens import Screen
from backend.app.models.theatre import Theatre

router = APIRouter(
    prefix="/public/screens",
    tags=["Public Screens"],
)


@router.get("/")
def get_public_screens(
    theatre_id: int,
    db: Session = Depends(get_db),
):
    theatre = db.get(Theatre, theatre_id)

    if theatre is None or not theatre.is_active:
        return []

    return db.scalars(
        select(Screen).where(
            Screen.theatre_id == theatre_id,
            Screen.screen_is_active.is_(True),
        )
    ).all()