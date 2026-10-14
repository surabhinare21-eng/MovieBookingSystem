
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.shows import Show
from backend.app.models.screens import Screen
from backend.app.models.theatre import Theatre
from backend.app.schemas.show import ShowOut

router = APIRouter(
    prefix="/public/shows",
    tags=["Public Shows"],
)


@router.get("/", response_model=list[ShowOut])
def get_public_shows(
    theatre_id: int | None = None,
    movie_id: int | None = None,
    show_date: date | None = None,
    db: Session = Depends(get_db),
):
    """Return scheduled shows for customers to browse."""

    query = (
        select(Show)
        .join(Screen, Show.screen_id == Screen.screen_id)
        .join(Theatre, Screen.theatre_id == Theatre.theatre_id)
        .where(
            Theatre.is_active.is_(True),
            Screen.screen_is_active.is_(True),
            Show.show_status.is_(True),
        )
    )

    if theatre_id is not None:
        query = query.where(Screen.theatre_id == theatre_id)

    if movie_id is not None:
        query = query.where(Show.movie_id == movie_id)

    if show_date is not None:
        query = query.where(
            Show.show_start_time >= show_date,
            Show.show_start_time < date.fromordinal(show_date.toordinal() + 1),
        )

    query = query.order_by(Show.show_start_time)

    return list(db.scalars(query).all())
