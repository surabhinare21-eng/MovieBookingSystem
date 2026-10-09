
"""
User model for the Movie Booking System (MTB).

Roles:
    ADMIN  - Administrative access
    VIEWER - Standard user access

Security:
    - Store only password hashes.
    - Normalize email addresses in the service layer.
    - Never expose hash_password in API responses.
"""

import enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum as SAEnum,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.time_stamp import Timestamp


class Role(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"


class User(Timestamp, Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    user_email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    phone_no: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        unique=True,
    )

    hash_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[Role] = mapped_column(
        SAEnum(Role, name="user_role_enum"),
        nullable=False,
        default=Role.CUSTOMER,
        server_default=text("'VIEWER'"),
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
    )

    __table_args__ = (
        CheckConstraint(
            "CHAR_LENGTH(TRIM(username)) > 0",
            name="ck_users_username_not_blank",
        ),
        CheckConstraint(
            "CHAR_LENGTH(TRIM(user_email)) > 0",
            name="ck_users_email_not_blank",
        ),
    )
