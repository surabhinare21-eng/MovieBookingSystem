import enum

from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey, Enum,
    UniqueConstraint, CheckConstraint, Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.common import TimestampMixin


class SeatType(str, enum.Enum):
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"


class City(Base):
    __tablename__ = "cities"

    city_id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String(100), nullable=False, unique=True)

    # one city -> many theatres
    theatres = relationship("Theatre", back_populates="city")


class Theatre(TimestampMixin, Base):
    __tablename__ = "theatres"

    theatre_id = Column(Integer, primary_key=True, index=True)
    theatre_name = Column(String(150), nullable=False)
    theatre_address = Column(Text, nullable=True)
    contact_info = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    city_id = Column(Integer, ForeignKey("cities.city_id"), nullable=False)

    # theatre.city -> one city, theatre.screens -> list of screens
    city = relationship("City", back_populates="theatres")
    screens = relationship("Screen", back_populates="theatre")

    __table_args__ = (
        UniqueConstraint("theatre_name", "city_id", name="uq_theatre_name_per_city"),
    )


class Screen(Base):
    __tablename__ = "screens"

    screen_id = Column(Integer, primary_key=True, index=True)
    screen_number = Column(String(20), nullable=False)
    total_rows = Column(Integer, nullable=False)
    total_cols = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    theatre_id = Column(Integer, ForeignKey("theatres.theatre_id"), nullable=False)

    theatre = relationship("Theatre", back_populates="screens")
    seats = relationship("Seat", back_populates="screen", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("screen_number", "theatre_id", name="uq_screen_number_per_theatre"),
        CheckConstraint("total_rows > 0", name="ck_screen_rows_positive"),
        CheckConstraint("total_cols > 0", name="ck_screen_cols_positive"),
    )


class Seat(Base):
    __tablename__ = "seats"

    seat_id = Column(Integer, primary_key=True, index=True)
    row_no = Column(Integer, nullable=False)
    col_no = Column(Integer, nullable=False)
    seat_label = Column(String(10), nullable=False)   # e.g. "A1"
    seat_type = Column(Enum(SeatType), default=SeatType.REGULAR, nullable=False)

    screen_id = Column(Integer, ForeignKey("screens.screen_id"), nullable=False)

    # seat.screen -> the one screen this seat belongs to
    screen = relationship("Screen", back_populates="seats")

    __table_args__ = (
        UniqueConstraint("screen_id", "row_no", "col_no", name="uq_seat_position_per_screen"),
    )


class Genre(Base):
    __tablename__ = "genres"

    genre_id = Column(Integer, primary_key=True, index=True)
    genre_name = Column(String(50), nullable=False, unique=True)

    # many-to-many through movie_genre
    movies = relationship("Movie", secondary="movie_genre", back_populates="genres")


class Movie(Base):
    __tablename__ = "movies"

    movie_id = Column(Integer, primary_key=True, index=True)
    movie_title = Column(String(200), nullable=False, index=True)
    movie_description = Column(Text, nullable=True)
    movie_language = Column(String(50), nullable=True)
    movie_poster_url = Column(String(500), nullable=True)
    movie_rating = Column(String(10), nullable=True)            # e.g. "U/A"
    movie_duration_min = Column(Integer, nullable=False)        # scheduling depends on this
    is_active = Column(Boolean, default=True, nullable=False)

    genres = relationship("Genre", secondary="movie_genre", back_populates="movies")

    __table_args__ = (
        CheckConstraint("movie_duration_min > 0", name="ck_movie_duration_positive"),
    )


class MovieGenre(Base):
    """Junction table: one movie has many genres, one genre has many movies."""
    __tablename__ = "movie_genre"

    movie_id = Column(Integer, ForeignKey("movies.movie_id"), primary_key=True)
    genre_id = Column(Integer, ForeignKey("genres.genre_id"), primary_key=True)