from pydantic import BaseModel, ConfigDict, Field


class ScreenCreate(BaseModel):
    screen_is_active: bool = True
    total_rows: int = Field(default=0, ge=0)
    total_cols: int = Field(default=0, ge=0)


class ScreenUpdate(BaseModel):
    screen_is_active: bool | None = None
    total_rows: int | None = Field(default=None, ge=0)
    total_cols: int | None = Field(default=None, ge=0)


class ScreenOut(BaseModel):
    screen_id: int
    theatre_id: int
    screen_is_active: bool
    total_rows: int
    total_cols: int

    model_config = ConfigDict(from_attributes=True)
