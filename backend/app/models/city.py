from datetime import datetime
from typing import TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, String, func, text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base


if TYPE_CHECKING:
    from backend.app.models.theatre import Theatre


class City(Base):
    __tablename__ = "cities"
    city_id: Mapped[int]= mapped_column(primary_key=True,autoincrement=True)
    name: Mapped[str]= mapped_column(String(100),nullable=False)
    is_active:Mapped[bool]= mapped_column(Boolean, default=True, server_default=text("1"), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=7), nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=7), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    theatres: Mapped[list["Theatre"]] = relationship(
        "Theatre",
        back_populates="city",
    )
    