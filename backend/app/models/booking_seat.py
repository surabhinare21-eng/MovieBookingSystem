from sqlalchemy import Boolean, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class BookingSeat(Base):
    """A seat assigned to a booking after successful payment."""

    __tablename__ = "booking_seats"

    booking_seat_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("BOOKINGS.booking_id"), nullable=False, index=True
    )
    seat_id: Mapped[int] = mapped_column(
        ForeignKey("seats.seat_id"), nullable=False
    )
    show_id: Mapped[int] = mapped_column(
        ForeignKey("shows.show_id"), nullable=False
    )
    price_paid: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
