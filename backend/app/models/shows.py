
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.show_enums import ShowLanguages, ShowFormat


class Show(Base):
    __tablename__ = "shows"

    show_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    show_start_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    show_end_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    show_status: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    show_language: Mapped[ShowLanguages] = mapped_column(
        SQLEnum(ShowLanguages),
        nullable=False
    )

    show_format: Mapped[ShowFormat] = mapped_column(
        SQLEnum(ShowFormat),
        default=ShowFormat.D2,
        nullable=False
    )

    screen_id: Mapped[int] = mapped_column(
        ForeignKey("screens.screen_id"),
        nullable=False
    )

    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.movie_id"),
        nullable=False
    )

    screen: Mapped["Screen"] = relationship(
        "Screen",
        back_populates="shows"
    )

    movie: Mapped["Movie"] = relationship(
        "Movie",
        back_populates="shows"
    )

