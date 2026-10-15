from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.city import City
from backend.app.schemas.admin import CityOut

router = APIRouter(prefix="/cities", tags=["Public Cities"])


@router.get("/public", response_model=list[CityOut])
def list_public_cities(
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = select(City).where(City.is_active.is_(True))
    if q and q.strip():
        query = query.where(City.name.icontains(q.strip(), autoescape=True))
    return list(db.scalars(query.order_by(City.name)))