
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


class Seat(Base):
    __tablename__ = "seats"

    seat_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    screen_id = Column(
        Integer,
        ForeignKey("screens.screen_id"),
        nullable=False,
    )

    row_no = Column(Integer, nullable=False)
    col_no = Column(Integer, nullable=False)

    seat_label = Column(
        String(10),
        nullable=False,
    )

    seat_type = Column(
        String(20),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "screen_id",
            "row_no",
            "col_no",
            name="uq_screen_seat_position",
        ),
        UniqueConstraint(
            "screen_id",
            "seat_label",
            name="uq_screen_seat_label",
        ),
    )

    screen = relationship("Screen")


class SeatLock(Base):
    __tablename__ = "seat_lock"

    lock_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    show_id = Column(
        Integer,
        ForeignKey("shows.show_id"),
        nullable=False,
    )

    seat_id = Column(
        Integer,
        ForeignKey("seats.seat_id"),
        nullable=False,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
    )

    screen_id = Column(
        Integer,
        ForeignKey("screens.screen_id"),
        nullable=False,
    )

    locked_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    expires_at = Column(
        DateTime,
        nullable=False,
    )

    lock_status = Column(
        String(20),
        nullable=False,
        default="ACTIVE",
    )

    __table_args__ = (
        Index(
            "ix_seat_lock_show_seat",
            "show_id",
            "seat_id",
        ),
    )

    show = relationship("Show")
    seat = relationship("Seat")
    user = relationship("User")
    screen = relationship("Screen")
