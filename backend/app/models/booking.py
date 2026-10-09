"""
STARTER for Nischay's module: review and adjust before using.
"""
import enum

from sqlalchemy import (
    Column, Integer, DateTime, ForeignKey, Enum,
    Index, UniqueConstraint, DECIMAL,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.common import TimestampMixin


class BookingStatus(str, enum.Enum):
    # Matches the BRD state machine
    SEAT_SELECTED = "SEAT_SELECTED"
    SEAT_LOCKED = "SEAT_LOCKED"
    BOOKED = "BOOKED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class LockStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"
    EXPIRED = "EXPIRED"
    CONVERTED = "CONVERTED"   # lock turned into a confirmed booking


class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    show_id = Column(Integer, ForeignKey("shows.show_id"), nullable=False)
    booking_status = Column(Enum(BookingStatus), default=BookingStatus.SEAT_SELECTED, nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)

    # Optimistic locking: SQLAlchemy bumps this on every update and raises
    # StaleDataError if two transactions change the same booking at once.
    version = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {"version_id_col": version}

    # One-way links across modules (no back_populates)
    user = relationship("User")
    show = relationship("Show")
    seats = relationship("BookingSeat", back_populates="booking", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_bookings_user_created", "user_id", "created_at"),
        Index("ix_bookings_show_status", "show_id", "booking_status"),
    )


class BookingSeat(Base):
    __tablename__ = "booking_seats"

    booking_seat_id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.seat_id"), nullable=False)
    show_id = Column(Integer, ForeignKey("shows.show_id"), nullable=False)   # repeated on purpose
    price_paid = Column(DECIMAL(10, 2), nullable=False)

    # MySQL has no partial unique index, so: active_key = 1 while the seat is
    # held/booked, NULL once cancelled/expired. MySQL allows many NULLs in a
    # unique index, so released seats can be booked again.
    active_key = Column(Integer, nullable=True, default=1)

    booking = relationship("Booking", back_populates="seats")

    __table_args__ = (
        UniqueConstraint("show_id", "seat_id", "active_key", name="uq_active_seat_per_show"),
    )

    @property
    def is_active(self) -> bool:
        return self.active_key is not None


class SeatLock(Base):
    __tablename__ = "seat_locks"

    lock_id = Column(Integer, primary_key=True, index=True)
    show_id = Column(Integer, ForeignKey("shows.show_id"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.seat_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    lock_status = Column(Enum(LockStatus), default=LockStatus.ACTIVE, nullable=False)
    locked_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    # Same trick: 1 while ACTIVE, NULL otherwise. Two viewers cannot both
    # hold an active lock on the same seat for the same show.
    active_key = Column(Integer, nullable=True, default=1)

    __table_args__ = (
        UniqueConstraint("show_id", "seat_id", "active_key", name="uq_active_lock_per_seat"),
        # Backs the expiry sweeper
        Index("ix_seat_locks_status_expiry", "lock_status", "expires_at"),
    )