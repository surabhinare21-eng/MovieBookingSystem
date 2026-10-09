
"""
Show and show-pricing models for the Movie Booking System.

Dependencies:
    - app.core.database.Base
    - app.models.time_stamp.Timestamp
    - app.models.catalog.SeatType
    - Catalogue models: Movie and Screen
"""

import enum
from datetime import datetime
from decimal import Decimal
from app.schemas.show import ShowStatus
from sqlalchemy import (
    CheckConstraint,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.time_stamp import Timestamp
from app.models.catalog import SeatType
from app.models.catalog import Movie, Screen


class Show(Timestamp, Base):
    __tablename__ = "shows"

    show_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    show_start_time: Mapped[datetime] = mapped_column(
        nullable=False
    )
    show_end_time: Mapped[datetime] = mapped_column(
        nullable=False
    )

    show_status: Mapped[ShowStatus] = mapped_column(
        SAEnum(ShowStatus, name="show_status_enum"),
        nullable=False,
        default=ShowStatus.SCHEDULED,
        server_default=text("'SCHEDULED'"),
    )

    show_language: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    show_format: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    screen_id: Mapped[int] = mapped_column(
        ForeignKey("screens.screen_id", ondelete="RESTRICT"),
        nullable=False,
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.movie_id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Relationships to catalogue models.
    movie: Mapped["Movie"] = relationship("Movie")
    screen: Mapped["Screen"] = relationship("Screen")

    # Pricing records owned by this show.
    pricing: Mapped[list["ShowPricing"]] = relationship(
        "ShowPricing",
        back_populates="show",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index(
            "ix_shows_screen_time",
            "screen_id",
            "show_start_time",
            "show_end_time",
        ),
        Index(
            "ix_shows_movie_start",
            "movie_id",
            "show_start_time",
        ),
        Index(
            "ix_shows_status_start",
            "show_status",
            "show_start_time",
        ),
        CheckConstraint(
            "show_end_time > show_start_time",
            name="ck_show_end_after_start",
        ),
    )


class ShowPricing(Timestamp, Base):
    __tablename__ = "show_pricing"

    pricing_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    show_id: Mapped[int] = mapped_column(
        ForeignKey("shows.show_id", ondelete="CASCADE"),
        nullable=False,
    )

    seat_type: Mapped[SeatType] = mapped_column(
        SAEnum(SeatType, name="seat_type_enum"),
        nullable=False,
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    show: Mapped["Show"] = relationship(
        "Show",
        back_populates="pricing",
    )

    __table_args__ = (
        UniqueConstraint(
            "show_id",
            "seat_type",
            name="uq_pricing_per_seat_type",
        ),
        CheckConstraint(
            "subtotal >= 0",
            name="ck_pricing_non_negative",
        ),
        Index("ix_show_pricing_show", "show_id"),
    )
