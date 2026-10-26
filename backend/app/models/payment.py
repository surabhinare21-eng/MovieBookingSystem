from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    Numeric,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class Status(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Payment(Base):
    __tablename__ = "PAYMENT"

    payment_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    booking_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("BOOKINGS.booking_id"),
        nullable=False,
    )

    final_amount: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    payment_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    payment_status: Mapped[Status] = mapped_column(
        String(20),
        default=Status.PENDING.value,
        nullable=False,
    )

    transaction_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
    )

    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )
    razorpay_order_id: Mapped[str | None] = mapped_column(
    String(100),
    nullable=True,
    unique=True,
    )

    razorpay_payment_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
    )