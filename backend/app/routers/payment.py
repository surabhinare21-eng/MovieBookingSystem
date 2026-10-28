from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.session import get_db
from backend.app.models.booking import Booking
from backend.app.models.payment import Payment
from backend.app.models.shows import Show
from backend.app.models.screens import Screen
from backend.app.models.theatre import Theatre
from backend.app.models.movies import Movie
from backend.app.models.seat import Seat, SeatLock
from backend.app.services.payment_service import (
    create_payment_order,
    verify_payment,
)
from backend.app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


@router.post("/create-order/{booking_id}")
def create_order(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a Razorpay order for an existing booking.
    """

    booking = (
        db.query(Booking)
        .filter(Booking.booking_id == booking_id)
        .first()
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found",
        )


    if booking.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot pay for this booking",
        )

    existing_payment = (
        db.query(Payment)
        .filter(
            Payment.booking_id == booking_id,
            Payment.payment_status == "SUCCESS",
        )
        .first()
    )

    if existing_payment:
        raise HTTPException(
            status_code=409,
            detail="Booking has already been paid",
        )

    return create_payment_order(db, booking)


@router.post("/verify")
def verify_order_payment(
    request: VerifyPaymentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Verify a Razorpay payment after Checkout completes.
    """

    payment = (
        db.query(Payment)
        .filter(
            Payment.razorpay_order_id
            == request.razorpay_order_id
        )
        .first()
    )

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment order not found",
        )

    booking = (
        db.query(Booking)
        .filter(
            Booking.booking_id == payment.booking_id
        )
        .first()
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found",
        )

    if booking.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot verify this payment",
        )

    return verify_payment(
        db=db,
        razorpay_order_id=request.razorpay_order_id,
        razorpay_payment_id=request.razorpay_payment_id,
        razorpay_signature=request.razorpay_signature,
    )


def _latest_payment(db: Session, booking_id: int):
    """Return the SUCCESS payment for a booking, else its newest attempt."""
    payments = (
        db.query(Payment)
        .filter(Payment.booking_id == booking_id)
        .order_by(Payment.payment_id.desc())
        .all()
    )
    for payment in payments:
        if payment.payment_status == "SUCCESS":
            return payment
    return payments[0] if payments else None


def _payment_fields(payment) -> dict:
    """Payment fields in the shape the Streamlit pages read."""
    if payment is None:
        return {
            "payment_status": "PENDING",
            "amount": None,
            "payment_type": None,
            "paid_at": None,
            "transaction_id": None,
        }
    return {
        "payment_status": payment.payment_status,
        "amount": str(payment.final_amount),
        "payment_type": payment.payment_type,
        "paid_at": (
            payment.paid_at.strftime("%d %b %Y, %I:%M %p")
            if payment.paid_at else None
        ),
        "transaction_id": payment.razorpay_payment_id,
    }


def _seat_labels(db: Session, booking: Booking) -> list[str]:
    """
    Find the seats of a booking.

    Bookings have no direct link to seats, but the seat holds and the
    booking are created together in one transaction, so the holds for
    the same user and show with almost the same timestamp belong to it.
    """
    window = timedelta(seconds=10)
    rows = (
        db.query(Seat.seat_label)
        .join(SeatLock, SeatLock.seat_id == Seat.seat_id)
        .filter(
            SeatLock.user_id == booking.user_id,
            SeatLock.show_id == booking.show_id,
            SeatLock.lock_status == "CONFIRMED",
            SeatLock.locked_at >= booking.created_at - window,
            SeatLock.locked_at <= booking.created_at + window,
        )
        .order_by(Seat.row_no, Seat.col_no)
        .all()
    )
    return [label for (label,) in rows]


@router.get("/my-bookings")
def my_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Return the logged-in customer's paid bookings, newest first."""

    rows = (
        db.query(Booking, Movie, Theatre, Screen, Show)
        .join(Show, Show.show_id == Booking.show_id)
        .join(Movie, Movie.movie_id == Show.movie_id)
        .join(Screen, Screen.screen_id == Show.screen_id)
        .join(Theatre, Theatre.theatre_id == Screen.theatre_id)
        .filter(Booking.user_id == current_user.user_id)
        .order_by(Booking.booking_id.desc())
        .all()
    )

    result = []
    for booking, movie, theatre, screen, show in rows:
        payment = _latest_payment(db, booking.booking_id)

        if payment is None or payment.payment_status != "SUCCESS":
            continue

        result.append({
            "booking_id": booking.booking_id,
            "movie_name": movie.movie_title,
            "theatre_name": theatre.name,
            "screen_name": screen.screen_name,
            "show_time": show.show_start_time.strftime("%d %b %Y, %I:%M %p"),
            "seat_labels": _seat_labels(db, booking),
            **_payment_fields(payment),
        })

    return result



@router.get("/booking/{booking_id}")
def booking_payment_status(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Return the payment status of one booking owned by the user."""

    booking = db.get(Booking, booking_id)

    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot view this booking",
        )

    payment = _latest_payment(db, booking_id)
    return {
        "booking_id": booking_id,
        **_payment_fields(payment),
    }