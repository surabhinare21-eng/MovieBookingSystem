from sqlalchemy import text,String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base
from backend.app.models.show_enums import ShowLanguages, ShowFormat
from sqlalchemy import Time



class Movie(Base):
    __tablename__ = "movies"

    movie_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    movie_title : Mapped[str] = mapped_column(String(255), nullable=False)
    movie_description : Mapped[str] = mapped_column(String(255), nullable=False)
    
    movie_status: Mapped[str] = mapped_column(String(100), nullable=False)
    
    movie_language: Mapped[ShowLanguages] = mapped_column(nullable=False)
    movie_poster_url : Mapped[str] = mapped_column(String(50), nullable=False)
    
    movie_rating : Mapped[int] = mapped_column(Integer)
    movie_duration : Mapped[Time] = mapped_column(Time, nullable=False)
    

# Inside class Movie(Base):

    shows: Mapped[list["Show"]] = relationship(
        "Show",
        back_populates="movie"
    )
