
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.seat import (
    SeatForShowOut,
    SeatLockCreate,
    SeatLockOut,
)
from backend.app.services import seat_service

router = APIRouter(prefix="/seats", tags=["Seats"])


@router.get(
    "/show/{show_id}",
    response_model=list[SeatForShowOut],
)
def get_show_seats(
    show_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    seats = seat_service.get_seats_for_show(db, show_id)

    if seats is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Show not found.",
        )

    return seats


@router.post(
    "/lock",
    response_model=list[SeatLockOut],
    status_code=status.HTTP_201_CREATED,
)
def lock_show_seats(
    request: SeatLockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return seat_service.lock_seats_for_show(
            db=db,
            show_id=request.show_id,
            seat_ids=request.seat_ids,
            user_id=current_user.user_id,
        )

    except ValueError as exc:
        message = str(exc)

        if "already booked or held" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from exc


@router.post("/release")
def release_show_seats(
    request: SeatLockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        released_count = seat_service.release_seats_for_show(
            db=db,
            show_id=request.show_id,
            seat_ids=request.seat_ids,
            user_id=current_user.user_id,
        )

        return {
            "message": "Seat holds released.",
            "released_count": released_count,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
        
@router.post("/generate/{screen_id}")
def generate_screen_seats(
    screen_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    seats = seat_service.generate_seats_for_screen(
        db=db,
        screen_id=screen_id,
    )

    if seats is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screen not found.",
        )

    return {
        "message": "Seats generated successfully.",
        "screen_id": screen_id,
        "total_seats": len(seats),
    }
