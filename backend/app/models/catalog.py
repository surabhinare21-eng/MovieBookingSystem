
"""
Catalogue models for the Movie Booking System (MTB).

Entities:
    City -> Theatre -> Screen -> Seat
    Movie <-> Genre (many-to-many)

Keep all models on the shared SQLAlchemy Base.
"""

import enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.time_stamp import Timestamp


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SeatType(str, enum.Enum):
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"


# ---------------------------------------------------------------------------
# City
# ---------------------------------------------------------------------------

class City(Base):
    __tablename__ = "cities"

    city_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city_name: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )

    theatres: Mapped[list["Theatre"]] = relationship(
        "Theatre",
        back_populates="city",
        passive_deletes=True,
    )


# ---------------------------------------------------------------------------
# Theatre
# ---------------------------------------------------------------------------

class Theatre(Timestamp, Base):
    __tablename__ = "theatres"

    theatre_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    theatre_name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )
    theatre_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_info: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
    )
    city_id: Mapped[int] = mapped_column(
        ForeignKey("cities.city_id", ondelete="RESTRICT"),
        nullable=False,
    )

    city: Mapped["City"] = relationship(
        "City", back_populates="theatres"
    )
    screens: Mapped[list["Screen"]] = relationship(
        "Screen",
        back_populates="theatre",
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "theatre_name",
            "city_id",
            name="uq_theatre_name_per_city",
        ),
        Index("ix_theatres_city_active", "city_id", "is_active"),
    )


# ---------------------------------------------------------------------------
# Screen
# ---------------------------------------------------------------------------

class Screen(Base):
    __tablename__ = "screens"

    screen_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    screen_number: Mapped[str] = mapped_column(
        String(20), nullable=False
    )
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    total_cols: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
    )
    theatre_id: Mapped[int] = mapped_column(
        ForeignKey("theatres.theatre_id", ondelete="RESTRICT"),
        nullable=False,
    )

    theatre: Mapped["Theatre"] = relationship(
        "Theatre", back_populates="screens"
    )
    seats: Mapped[list["Seat"]] = relationship(
        "Seat",
        back_populates="screen",
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "screen_number",
            "theatre_id",
            name="uq_screen_number_per_theatre",
        ),
        CheckConstraint(
            "total_rows > 0", name="ck_screen_rows_positive"
        ),
        CheckConstraint(
            "total_cols > 0", name="ck_screen_cols_positive"
        ),
        Index("ix_screens_theatre_active", "theatre_id", "is_active"),
    )


# ---------------------------------------------------------------------------
# Seat
# ---------------------------------------------------------------------------

class Seat(Base):
    __tablename__ = "seats"

    seat_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    row_no: Mapped[int] = mapped_column(Integer, nullable=False)
    col_no: Mapped[int] = mapped_column(Integer, nullable=False)
    seat_label: Mapped[str] = mapped_column(
        String(10), nullable=False
    )
    seat_type: Mapped[SeatType] = mapped_column(
        SAEnum(SeatType, name="seat_type_enum"),
        nullable=False,
        default=SeatType.REGULAR,
        server_default=text("'REGULAR'"),
    )
    screen_id: Mapped[int] = mapped_column(
        ForeignKey("screens.screen_id", ondelete="RESTRICT"),
        nullable=False,
    )

    screen: Mapped["Screen"] = relationship(
        "Screen", back_populates="seats"
    )

    __table_args__ = (
        UniqueConstraint(
            "screen_id",
            "row_no",
            "col_no",
            name="uq_seat_position_per_screen",
        ),
        UniqueConstraint(
            "screen_id",
            "seat_label",
            name="uq_seat_label_per_screen",
        ),
        CheckConstraint("row_no > 0", name="ck_seat_row_positive"),
        CheckConstraint("col_no > 0", name="ck_seat_col_positive"),
        Index("ix_seats_screen", "screen_id"),
    )


# ---------------------------------------------------------------------------
# Genre
# ---------------------------------------------------------------------------

class Genre(Base):
    __tablename__ = "genres"

    genre_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    genre_name: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True
    )

    movies: Mapped[list["Movie"]] = relationship(
        "Movie",
        secondary="movie_genre",
        back_populates="genres",
        passive_deletes=True,
    )


# ---------------------------------------------------------------------------
# Movie
# ---------------------------------------------------------------------------

class Movie(Base):
    __tablename__ = "movies"

    movie_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    movie_title: Mapped[str] = mapped_column(
        String(200), nullable=False
    )
    movie_description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    movie_language: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    movie_poster_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    movie_rating: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )
    movie_duration_min: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
    )

    genres: Mapped[list["Genre"]] = relationship(
        "Genre",
        secondary="movie_genre",
        back_populates="movies",
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint(
            "movie_duration_min > 0",
            name="ck_movie_duration_positive",
        ),
        Index("ix_movies_active_title", "is_active", "movie_title"),
    )


# ---------------------------------------------------------------------------
# MovieGenre: many-to-many association table
# ---------------------------------------------------------------------------

class MovieGenre(Base):
    __tablename__ = "movie_genre"

    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.movie_id", ondelete="CASCADE"),
        primary_key=True,
    )
    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genres.genre_id", ondelete="CASCADE"),
        primary_key=True,
    )
