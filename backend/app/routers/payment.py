from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.session import get_db
from backend.app.models.booking import Booking
from backend.app.models.payment import Payment
from backend.app.services.payment import (
    create_payment_order,
    verify_payment,
)
from backend.app.core.security import get_current_user


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

    # IMPORTANT:
    # Replace user_id with the actual ownership field
    # in your Booking model.
    if booking.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot pay for this booking",
        )

    # Prevent creating another order for a paid booking.
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

    # Locate the order and verify booking ownership
    # before allowing verification.
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

    # Replace user_id with your actual ownership field.
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