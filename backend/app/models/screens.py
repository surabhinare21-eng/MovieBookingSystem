
from sqlalchemy import Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.theatre import Theatre
from backend.app.models.show_enums import ShowLanguages, ShowFormat
from backend.app.models.shows import Show



class Screen(Base):
    __tablename__ = "screens"

    screen_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    theatre_id: Mapped[int] = mapped_column(
        ForeignKey("theatres.theatre_id"),
        nullable=False
    )

    screen_is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    total_rows: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    total_cols: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    theatre: Mapped["Theatre"] = relationship(
        back_populates="screens"
    )

    shows: Mapped[list["Show"]] = relationship(
        "Show",
        back_populates="screen"
    )

