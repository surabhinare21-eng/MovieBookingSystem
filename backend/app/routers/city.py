from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.permissions import require_roles
from backend.app.db.session import get_db
from backend.app.models.theatre import Theatre
from backend.app.models.city import City
from backend.app.models.user import Role, User
from backend.app.schemas.admin import (
    ActiveStatus,
    TheatreAdminCreate,
    TheatreCreate,
    TheatreOut,
    UserAdminOut,
    CityOut,
    CityCreate,
    CityUpdate
)
from backend.app.services import admin_service

super_admin_only = require_roles(Role.SUPER_ADMIN)

router = APIRouter(
    prefix="/root-admin",
    tags=["Root Admin (SUPER_ADMIN)"],
    dependencies=[Depends(super_admin_only)],
)

@router.post("/cities",response_model=CityOut,status_code=status.HTTP_201_CREATED)
def add_city(payload:CityCreate, db: Session = Depends(get_db), current_user = Depends(super_admin_only)):
    try:
        return admin_service.create_city(db,payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=str(exc)) from exc
        
@router.get("/cities", response_model=list[CityOut])
def list_cities(db: Session = Depends(get_db), current_user=Depends(super_admin_only)):
    return list(db.scalars(select(City).order_by(City.city_id)))

@router.patch("/cities/{city_id}/status", response_model=CityOut)
def change_theatre_status(city_id: int, payload: ActiveStatus, db: Session = Depends(get_db)):
    try:
        return admin_service.set_city_active(db, city_id, payload.is_active)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
   


@router.delete("/cities/{city_id}")
def delete_city(
    city_id: int,
    db: Session = Depends(get_db),
):
    city = db.get(City, city_id)

    if city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found.",
        )

    try:
        db.delete(city)
        db.commit()

        return {
            "message": f"City '{city.name}' deleted successfully."
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Cannot delete this city because it is "
                "referenced by another record, such as a theatre."
            ),
        )