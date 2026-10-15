from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.city import City
from backend.app.models.movies import Movie
from backend.app.models.screens import Screen
from backend.app.models.shows import Show
from backend.app.models.theatre import Theatre
from backend.app.schemas.movies import MovieOut

router = APIRouter(prefix="/public/movies", tags=["Public Movies"])


@router.get("/", response_model=list[MovieOut])
def get_movies_in_city(city_id: int, db: Session = Depends(get_db)):
    city = db.get(City, city_id)
    if city is None or not city.is_active:
        return []

    query = (
        select(Movie)
        .join(Show, Show.movie_id == Movie.movie_id)
        .join(Screen, Show.screen_id == Screen.screen_id)
        .join(Theatre, Screen.theatre_id == Theatre.theatre_id)
        .where(
            Theatre.city_id == city_id,
            Theatre.is_active.is_(True),
            Screen.screen_is_active.is_(True),
            Show.show_status.is_(True),
            Show.show_start_time > datetime.now(),
            func.upper(Movie.movie_status) == "ACTIVE",
        )
        .distinct()
        .order_by(Movie.movie_title)
    )
    return list(db.scalars(query).all())