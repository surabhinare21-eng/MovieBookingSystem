import enum

from sqlalchemy import Column, Integer, String, Boolean, Enum

from app.core.database import Base
from app.models.common import TimestampMixin


class Role(str, enum.Enum):
    # The BRD defines exactly two roles.
    ADMIN = "ADMIN"
    VIEWER = "VIEWER"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    user_email = Column(String(100), nullable=False, unique=True)   # store lowercase
    phone_no = Column(String(20), nullable=True, unique=True)       # optional; many NULLs allowed
    hash_password = Column(String(255), nullable=False)             # never returned in responses
    role = Column(Enum(Role), default=Role.VIEWER, nullable=False)  # self-registration = VIEWER
    is_active = Column(Boolean, default=True, nullable=False)