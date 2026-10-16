
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------- Seat Schemas ----------

class SeatCreate(BaseModel):
    screen_id: int = Field(gt=0)
    row_no: int = Field(gt=0)
    col_no: int = Field(gt=0)
    seat_label: str = Field(min_length=1, max_length=10)
    seat_type: Literal["GOLD", "PLATINUM"]


class SeatUpdate(BaseModel):
    row_no: int | None = Field(default=None, gt=0)
    col_no: int | None = Field(default=None, gt=0)
    seat_label: str | None = Field(
        default=None,
        min_length=1,
        max_length=10,
    )
    seat_type: Literal["GOLD", "PLATINUM"] | None = None


class SeatOut(BaseModel):
    seat_id: int
    screen_id: int
    row_no: int
    col_no: int
    seat_label: str
    seat_type: str

    model_config = ConfigDict(from_attributes=True)


# ---------- Show-Specific Seat Status ----------

class SeatForShowOut(SeatOut):
    seat_status: Literal["AVAILABLE", "HOLD", "BOOKED"]


# ---------- Seat Lock Schemas ----------

class SeatLockCreate(BaseModel):
    show_id: int = Field(gt=0)
    seat_ids: list[int] = Field(min_length=1,max_length=10)


class SeatLockOut(BaseModel):
    lock_id: int
    show_id: int
    seat_id: int
    user_id: int
    screen_id: int
    locked_at: datetime
    expires_at: datetime
    lock_status: str

    model_config = ConfigDict(from_attributes=True)
