from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func, text
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum
from app.db.base import Base

class Role(str, Enum.enum):
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
    CUSTOMER = "CUSTOMER"

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    user_email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone_no = Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role : Mapped[Role] = mapped_column(String, default=Role.CUSTOMER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("1"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    
    
