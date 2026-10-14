
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.theatre import Theatre
from backend.app.models.city import City

router = APIRouter(
    prefix="/theatres",
    tags=["Public Theatres"],
)


@router.get("/public")
def get_public_theatres(
    city_id: int,
    db: Session = Depends(get_db),
):
    city = db.get(City, city_id)

    if city is None or not city.is_active:
        return []

    return db.scalars(
        select(Theatre).where(
            Theatre.city_id == city_id,
            Theatre.is_active.is_(True),
        ).order_by(Theatre.name)
    ).all()
