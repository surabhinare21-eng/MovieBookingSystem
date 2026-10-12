from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.permissions import require_roles
from backend.app.models.screens import Screen
from backend.app.models.shows import Show
from backend.app.models.theatre import Theatre
from backend.app.models.user import User, Role
from backend.app.db.session import get_db
from backend.app.schemas.show import (
    ShowCreate,
    ShowUpdate,
    ShowOut,
    ShowStatus,
)
from backend.app.services import show_service

admin_only = require_roles(Role.ADMIN)
router = APIRouter(prefix="/shows", tags=["Shows"])


def get_own_theatre(current_user: User, db: Session) -> Theatre:
    """Returns the active theatre assigned to the logged-in admin."""
    theatre = db.get(Theatre, current_user.theatre_id) if current_user.theatre_id else None
    if theatre is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No theatre assigned to this account.",
        )
    if not theatre.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your theatre has been deactivated.",
        )
    return theatre


def get_own_screen(
    screen_id: int,
    theatre: Theatre,
    db: Session,
) -> Screen:
    """Ensuring the theatre is the admins theatre."""
    screen = db.scalar(
        select(Screen).where(
            Screen.screen_id == screen_id,
            Screen.theatre_id == theatre.theatre_id,
        )
    )
    if screen is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screen not found in your theatre.",
        )
    return screen


def get_own_show(show_id: int, theatre: Theatre, db: Session) -> Show:
    """the show belong to the admin theatre"""
    show = db.scalar(
        select(Show)
        .join(Screen, Show.screen_id == Screen.screen_id)
        .where(
            Show.show_id == show_id,
            Screen.theatre_id == theatre.theatre_id,
        )
    )
    if show is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Show not found in your theatre.",
        )
    return show


@router.post("/", response_model=ShowOut, status_code=status.HTTP_201_CREATED)
def create_show(
    show: ShowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    theatre = get_own_theatre(current_user, db)
    get_own_screen(show.screen_id, theatre, db)
    try:
        return show_service.create_show(db, show)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/{show_id}", response_model=ShowOut)
def get_show(
    show_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    theatre = get_own_theatre(current_user, db)
    return get_own_show(show_id, theatre, db)


@router.get("/", response_model=list[ShowOut])
def get_all_shows(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    theatre = get_own_theatre(current_user, db)
    return list(
        db.scalars(
            select(Show)
            .join(Screen, Show.screen_id == Screen.screen_id)
            .where(Screen.theatre_id == theatre.theatre_id)
            .order_by(Show.show_id)
        )
    )


@router.patch("/{show_id}", response_model=ShowOut)
def update_show(
    show: ShowUpdate,
    show_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    theatre = get_own_theatre(current_user, db)
    get_own_show(show_id, theatre, db)
    get_own_screen(show.screen_id, theatre, db)
    try:
        return show_service.update_show(db, show_id, show)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch("/{show_id}/status", response_model=ShowOut)
def update_show_status(
    show_id: int,
    show: ShowStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    theatre = get_own_theatre(current_user, db)
    get_own_show(show_id, theatre, db)
    return show_service.update_show_status(db, show_id, show.show_status)
