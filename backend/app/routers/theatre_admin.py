from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.permissions import require_roles
from backend.app.db.session import get_db
from backend.app.models.theatre import Theatre
from backend.app.models.user import Role, User
from backend.app.schemas.admin import TheatreOut, TheatreUpdate

admin_only = require_roles(Role.ADMIN)

router = APIRouter(prefix="/theatre-admin", tags=["Theatre Admin (ADMIN)"])


def get_own_theatre(current_user: User, db: Session) -> Theatre:
    """The theatre always comes from the logged-in user, never from the client."""
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


@router.get("/my-theatre", response_model=TheatreOut)
def my_theatre(current_user: User = Depends(admin_only), db: Session = Depends(get_db)):
    return get_own_theatre(current_user, db)


@router.patch("/my-theatre", response_model=TheatreOut)
def update_my_theatre(
    payload: TheatreUpdate,
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    theatre = get_own_theatre(current_user, db)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(theatre, field, value)

    db.commit()
    db.refresh(theatre)
    return theatre