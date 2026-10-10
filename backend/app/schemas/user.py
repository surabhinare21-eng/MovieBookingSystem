from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from backend.app.models.user import Role


class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    user_email: EmailStr
    phone_no: str = Field(min_length=7, max_length=20)
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    user_id: int
    username: str
    user_email: EmailStr
    phone_no: str
    role: Role
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
