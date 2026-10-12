from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
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
def add_city(payload:CityCreate, db: Session = Depends(get_db)):
    try:
        return admin_service.create_city(db,payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=str(exc)) from exc
        
@router.get("/cities", response_model=list[CityOut])
def list_cities(db: Session = Depends(get_db)):
    return list(db.scalars(select(City).order_by(City.city_id)))


@router.patch("/cities/{city_id}/status", response_model=CityOut)
def change_theatre_status(city_id: int, payload: ActiveStatus, db: Session = Depends(get_db)):
    try:
        return admin_service.set_city_active(db, city_id, payload.is_active)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/theatres", response_model=TheatreOut, status_code=status.HTTP_201_CREATED)
def add_theatre(payload: TheatreCreate, db: Session = Depends(get_db)):
    try:
        return admin_service.create_theatre(db, payload.name, payload.city, payload.address)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/theatres", response_model=list[TheatreOut])
def list_theatres(db: Session = Depends(get_db)):
    return list(db.scalars(select(Theatre).order_by(Theatre.theatre_id)))


@router.patch("/theatres/{theatre_id}/status", response_model=TheatreOut)
def change_theatre_status(theatre_id: int, payload: ActiveStatus, db: Session = Depends(get_db)):
    try:
        return admin_service.set_theatre_active(db, theatre_id, payload.is_active)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/theatre-admins", response_model=UserAdminOut, status_code=status.HTTP_201_CREATED)
def add_theatre_admin(payload: TheatreAdminCreate, db: Session = Depends(get_db)):
    try:
        return admin_service.create_theatre_admin(
            db,
            username=payload.username,
            email=str(payload.user_email),
            phone_no=payload.phone_no,
            password=payload.password,
            theatre_id=payload.theatre_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/users", response_model=list[UserAdminOut])
def list_users(
    role: Role | None = None,
    skip: int = 0,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    query = select(User).order_by(User.user_id).offset(skip).limit(limit)
    if role is not None:
        query = query.where(User.role == role.value)
    return list(db.scalars(query))


@router.patch("/users/{user_id}/status", response_model=UserAdminOut)
def block_or_unblock_user(
    user_id: int,
    payload: ActiveStatus,
    acting_user: User = Depends(super_admin_only),
    db: Session = Depends(get_db),
):
    try:
        return admin_service.set_user_active(db, user_id, payload.is_active, acting_user)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc