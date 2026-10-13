from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.city import City

class Theatre(Base):
    __tablename__ = "theatres"

    theatre_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.city_id"),nullable=False
)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_info :Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=text("1"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
  

# Inside class Theatre(Base):

    screens: Mapped[list["Screen"]] = relationship(
        "Screen",
        back_populates="theatre"
    )
    city: Mapped["City"] = relationship(
    back_populates="theatres"
)
