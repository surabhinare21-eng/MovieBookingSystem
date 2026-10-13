from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.app.core.permissions import require_roles
from backend.app.db.session import get_db
from backend.app.models.theatre import Theatre
from backend.app.models.user import Role, User
from backend.app.schemas.screen import ScreenCreate, ScreenOut, ScreenUpdate
from backend.app.services import screen_service

admin_only = require_roles(Role.ADMIN)
router = APIRouter(prefix="/screens", tags=["Screens"])


def get_own_theatre(current_user: User, db: Session) -> Theatre:
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
):
    screen = screen_service.get_screen_by_id(db, screen_id, theatre.theatre_id)
    if screen is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screen not found in your theatre.",
        )
    return screen


@router.post("/", response_model=ScreenOut, status_code=status.HTTP_201_CREATED)
def create_screen(
    payload: ScreenCreate,
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    theatre = get_own_theatre(current_user, db)
    return screen_service.create_screen(db, theatre.theatre_id, payload)


@router.get("/", response_model=list[ScreenOut])
def get_all_screens(
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    theatre = get_own_theatre(current_user, db)
    return screen_service.get_screens_by_theatre(db, theatre.theatre_id)


@router.get("/{screen_id}", response_model=ScreenOut)
def get_screen(
    screen_id: int,
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    theatre = get_own_theatre(current_user, db)
    return get_own_screen(screen_id, theatre, db)


@router.patch("/{screen_id}", response_model=ScreenOut)
def update_screen(
    screen_id: int,
    payload: ScreenUpdate,
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    theatre = get_own_theatre(current_user, db)
    screen = get_own_screen(screen_id, theatre, db)
    return screen_service.update_screen(db, screen, payload)


@router.delete("/{screen_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_screen(
    screen_id: int,
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    theatre = get_own_theatre(current_user, db)
    screen = get_own_screen(screen_id, theatre, db)
    screen_service.delete_screen(db, screen)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
