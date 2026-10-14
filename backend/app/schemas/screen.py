from pydantic import BaseModel, ConfigDict, Field


class ScreenCreate(BaseModel):
   
    screen_name: str = Field(min_length=1, max_length=100)
    seat_layout_name: str = Field(min_length=1, max_length=20)
    screen_is_active: bool = False


class ScreenUpdate(BaseModel):
    theatre_id: int | None = Field(default=None, gt=0)
    screen_name: str | None = Field(default=None, min_length=1, max_length=100)
    seat_layout_name: str | None = Field(default=None, min_length=1, max_length=20)
    screen_is_active: bool | None = None


class ScreenOut(BaseModel):
    screen_id: int
    theatre_id: int
    screen_name: str
    seat_layout_name: str
    screen_is_active: bool

    model_config = ConfigDict(from_attributes=True)