from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from backend.app.schemas.user import PASSWORD_REGEX, UserOut

class CityCreate(BaseModel):
    name: str = Field(min_length = 2, max_length=200)    
    
class CityUpdate(BaseModel):
    name: str | None= Field(default=None,min_length=2,max_length=150)
    
class CityOut(BaseModel):
    name: str
    city_id : int
    is_active: bool
    model_config = {"from_attributes":True}
    
class TheatreCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    city: str = Field(min_length=2, max_length=100)
    address: str = Field(min_length=5, max_length=255)
    
    
class TheatreUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    address: str | None = Field(default=None, min_length=5, max_length=255)


class TheatreOut(BaseModel):
    theatre_id: int
    name: str
    city: str
    address: str
    is_active: bool

    model_config = {"from_attributes": True}

    @field_validator("city", mode="before")
    @classmethod
    def city_name_from_relationship(cls, value):
        return value.name if hasattr(value, "name") else value


class ActiveStatus(BaseModel):
    is_active: bool


class TheatreAdminCreate(BaseModel):
    model_config = ConfigDict(regex_engine="python-re")

    username: str = Field(min_length=2, max_length=100)
    user_email: EmailStr
    phone_no: str = Field(min_length=7, max_length=20)
    password: str = Field(min_length=8, max_length=12, pattern=PASSWORD_REGEX)
    theatre_id: int


class UserAdminOut(UserOut):
    theatre_id: int | None = None