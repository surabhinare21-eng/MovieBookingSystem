from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

import razorpay
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.payment import Payment, Status
from backend.app.models.booking import Booking
from backend.app.models.seat import SeatLock


razorpay_client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET,
    )
)


def create_payment_order(
    db: Session,
    booking,
):
    """
    Create a Razorpay order for an existing booking.

    The caller must verify that the booking belongs
    to the authenticated user and is eligible for payment.
    """

    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(
            status_code=503,
            detail=(
                "Razorpay is not configured. Set RAZORPAY_KEY_ID and "
                "RAZORPAY_KEY_SECRET in the backend .env file."
            ),
        )

    amount = Decimal(str(booking.total_amount))

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid booking amount",
        )

    # Razorpay expects INR in paise.
    amount_paise = int(
        (amount * 100).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )

    try:
        order = razorpay_client.order.create(
            data={
                "amount": amount_paise,
                "currency": "INR",
                "receipt": f"booking_{booking.booking_id}",
            }
        )
    except Exception as exc:
            print("Razorpay error:", repr(exc))
            raise HTTPException(
                status_code=502,
                detail=f"Unable to create Razorpay order: {exc}",
            ) from exc

    payment = Payment(
        booking_id=booking.booking_id,
        final_amount=amount,
        payment_type="RAZORPAY",
        payment_status=Status.PENDING.value,
        razorpay_order_id=order["id"],
    )

    try:
        db.add(payment)
        db.commit()
        db.refresh(payment)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to save payment record",
        )

    return {
        "payment_id": payment.payment_id,
        "booking_id": payment.booking_id,
        "razorpay_order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "payment_status": payment.payment_status,
    }


def verify_payment(
    db: Session,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
):
    """
    Verify Razorpay Checkout response and update payment.
    """

    payment = (
        db.query(Payment)
        .filter(
            Payment.razorpay_order_id == razorpay_order_id
        )
        .with_for_update()
        .first()
    )

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment order not found",
        )

    # Verify against the order ID already stored in our DB.
    try:
        razorpay_client.utility.verify_payment_signature(
            {
                "razorpay_order_id": payment.razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
        )
    except razorpay.errors.SignatureVerificationError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment signature",
        ) from exc

    # Fetch payment details from Razorpay to confirm status
    # and ensure the payment matches the stored order.
    try:
        gateway_payment = razorpay_client.payment.fetch(
            razorpay_payment_id
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to verify payment status with Razorpay",
        ) from exc

    if gateway_payment.get("order_id") != payment.razorpay_order_id:
        raise HTTPException(
            status_code=400,
            detail="Payment does not match the order",
        )

    expected_amount = int(
        (Decimal(str(payment.final_amount)) * 100).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )

    if gateway_payment.get("amount") != expected_amount:
        raise HTTPException(
            status_code=400,
            detail="Payment amount mismatch",
        )

    if gateway_payment.get("currency") != "INR":
        raise HTTPException(
            status_code=400,
            detail="Payment currency mismatch",
        )

    gateway_status = gateway_payment.get("status")

    if gateway_status != "captured":
        # A valid signature alone does not mean the
        # payment has been captured.
        raise HTTPException(
            status_code=409,
            detail=f"Payment is not captured: {gateway_status}",
        )

    # Make repeated successful verification requests safe.
    if payment.payment_status == Status.SUCCESS.value:
        if payment.razorpay_payment_id != razorpay_payment_id:
            raise HTTPException(
                status_code=409,
                detail="Payment already completed with another transaction",
            )

        return {
            "message": "Payment already verified",
            "payment_id": payment.payment_id,
            "payment_status": payment.payment_status,
        }

    if payment.payment_status != Status.PENDING.value:
        raise HTTPException(
            status_code=409,
            detail="Payment is not in a payable state",
        )

    payment.razorpay_payment_id = razorpay_payment_id
    payment.payment_status = Status.SUCCESS.value
    payment.paid_at = datetime.now()
    booking = db.get(Booking, payment.booking_id)
    if booking is not None:
        booking.status = "PAID"
        db.query(SeatLock).filter(
            SeatLock.show_id == booking.show_id,
            SeatLock.user_id == booking.user_id,
            SeatLock.lock_status == "ACTIVE",
        ).update(
            {"lock_status": "CONFIRMED"},
            synchronize_session=False,
        )

    try:
        db.commit()
        db.refresh(payment)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to update payment record",
        )

    return {
        "message": "Payment verified successfully",
        "payment_id": payment.payment_id,
        "booking_id": payment.booking_id,
        "payment_status": payment.payment_status,
        "razorpay_payment_id": payment.razorpay_payment_id,
        "paid_at": payment.paid_at,
    }