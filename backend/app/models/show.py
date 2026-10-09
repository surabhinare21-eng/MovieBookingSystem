import enum

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Enum,
    Index, CheckConstraint, UniqueConstraint, DECIMAL,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.common import TimestampMixin
from app.models.catalog import SeatType   # shared vocabulary, enum only


class ShowStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class Show(TimestampMixin, Base):
    __tablename__ = "shows"

    show_id = Column(Integer, primary_key=True, index=True)
    show_start_time = Column(DateTime, nullable=False)
    show_end_time = Column(DateTime, nullable=False)       # computed by the service, never sent by client
    show_status = Column(Enum(ShowStatus), default=ShowStatus.SCHEDULED, nullable=False)
    show_language = Column(String(50), nullable=False)
    show_format = Column(String(100), nullable=False)      # e.g. "2D", "3D", "IMAX"

    screen_id = Column(Integer, ForeignKey("screens.screen_id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.movie_id"), nullable=False)

    # One-way links to Catalog (no back_populates), so Catalog's files stay untouched.
    # They let list_shows() eager-load with selectinload.
    movie = relationship("Movie")
    screen = relationship("Screen")

    # Inside our own module, both sides are fine.
    pricing = relationship("ShowPricing", back_populates="show", cascade="all, delete-orphan")

    __table_args__ = (
        # Backs the overlap check: filter by screen, compare times.
        Index("ix_shows_screen_time", "screen_id", "show_start_time", "show_end_time"),
        # Backs list/filter by movie.
        Index("ix_shows_movie_start", "movie_id", "show_start_time"),
        CheckConstraint("show_end_time > show_start_time", name="ck_show_end_after_start"),
    )


class ShowPricing(Base):
    __tablename__ = "show_pricing"

    pricing_id = Column(Integer, primary_key=True, index=True)
    show_id = Column(Integer, ForeignKey("shows.show_id"), nullable=False)
    seat_type = Column(Enum(SeatType), nullable=False)
    subtotal = Column(DECIMAL(10, 2), nullable=False)

    show = relationship("Show", back_populates="pricing")

    __table_args__ = (
        # One price per seat type per show.
        UniqueConstraint("show_id", "seat_type", name="uq_pricing_per_seat_type"),
        CheckConstraint("subtotal >= 0", name="ck_pricing_non_negative"),
    )