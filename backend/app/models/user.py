from enum import Enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class Role(str, Enum):
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
    CUSTOMER = "CUSTOMER"

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    user_email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone_no: Mapped[str] = mapped_column(String(20), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(
        String(20),
        default=Role.CUSTOMER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("1"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    
    
