
import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.user import User
from app.models.show import Show
from app.core.database import Base
from app.models.time_stamp import Timestamp


class BookingStatus(str, enum.Enum):
    SEAT_SELECTED = "SEAT_SELECTED"
    SEAT_LOCKED = "SEAT_LOCKED"
    BOOKED = "BOOKED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class LockStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"
    EXPIRED = "EXPIRED"
    CONVERTED = "CONVERTED"


class Booking(Timestamp, Base):
    __tablename__ = "bookings"

    booking_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
    )
    show_id: Mapped[int] = mapped_column(
        ForeignKey("shows.show_id", ondelete="RESTRICT"),
        nullable=False,
    )
    booking_status: Mapped[BookingStatus] = mapped_column(
        SAEnum(BookingStatus, name="booking_status_enum"),
        nullable=False,
        default=BookingStatus.SEAT_SELECTED,
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )

    __mapper_args__ = {"version_id_col": version}

    user: Mapped["User"] = relationship("User")
    show: Mapped["Show"] = relationship("Show")
    seats: Mapped[list["BookingSeat"]] = relationship(
        "BookingSeat",
        back_populates="booking",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("ix_bookings_user_created", "user_id", "created_at"),
        Index("ix_bookings_show_status", "show_id", "booking_status"),
        CheckConstraint(
            "total_amount >= 0",
            name="ck_bookings_total_nonnegative",
        ),
    )


class BookingSeat(Base):
    __tablename__ = "booking_seats"

    booking_seat_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.booking_id", ondelete="RESTRICT"),
        nullable=False,
    )
    seat_id: Mapped[int] = mapped_column(
        ForeignKey("seats.seat_id", ondelete="RESTRICT"),
        nullable=False,
    )
    show_id: Mapped[int] = mapped_column(
        ForeignKey("shows.show_id", ondelete="RESTRICT"),
        nullable=False,
    )
    price_paid: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    active_key: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=1
    )

    booking: Mapped["Booking"] = relationship(
        "Booking", back_populates="seats"
    )

    __table_args__ = (
        UniqueConstraint(
            "show_id", "seat_id", "active_key",
            name="uq_active_seat_per_show",
        ),
        CheckConstraint(
            "price_paid >= 0",
            name="ck_booking_seat_price_nonnegative",
        ),
        CheckConstraint(
            "active_key IS NULL OR active_key = 1",
            name="ck_booking_seat_active_key",
        ),
    )

    @property
    def is_active(self) -> bool:
        return self.active_key == 1


class SeatLock(Base):
    __tablename__ = "seat_locks"

    lock_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )
    show_id: Mapped[int] = mapped_column(
        ForeignKey("shows.show_id", ondelete="RESTRICT"),
        nullable=False,
    )
    seat_id: Mapped[int] = mapped_column(
        ForeignKey("seats.seat_id", ondelete="RESTRICT"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
    )
    lock_status: Mapped[LockStatus] = mapped_column(
        SAEnum(LockStatus, name="seat_lock_status_enum"),
        nullable=False,
        default=LockStatus.ACTIVE,
    )
    locked_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )
    active_key: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=1
    )

    __table_args__ = (
        UniqueConstraint(
            "show_id", "seat_id", "active_key",
            name="uq_active_lock_per_seat",
        ),
        Index(
            "ix_seat_locks_status_expiry",
            "lock_status", "expires_at",
        ),
        CheckConstraint(
            "active_key IS NULL OR active_key = 1",
            name="ck_seat_lock_active_key",
        ),
        CheckConstraint(
            "expires_at > locked_at",
            name="ck_seat_lock_expiry",
        ),
    )
