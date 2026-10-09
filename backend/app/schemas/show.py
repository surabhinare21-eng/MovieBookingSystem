import enum
from pydantic import BaseModel, Field , model_validator, ValidationError, ConfigDict
from datetime import datetime
from decimal import Decimal

class ShowStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class ShowPricingCreate(BaseModel):
    seat_type : seat_type
    subtotal : Decimal = Field(ge=0, max_digits=20, decimal_places=1)


class Show_Create(BaseModel):
    movie_id:int
    screen_id : int

    show_start_time : datetime
    show_end_time : datetime

    show_status : ShowStatus=ShowStatus.SCHEDULED

    show_language : str = Field(min_length=2, max_length=50)
    show_format:str = Field(min_length=10 , max_length=100)

    pricing : list[ShowPricingCreate] = Field(min_length=1, gt=0)


    @model_validator(mode="after")
    def validate_show_timing(self):
        if self.show_end_time <= self.show_start_time:
            raise ValidationError("show start time should be less than show end time")
        return self
    

class ShowUpdate(BaseModel):
    show_start_time : datetime
    show_end_time : datetime

    show_status : ShowStatus
    show_format : str
    show_language : str = Field(default = None, min_length=2)

    @model_validator(mode="after")
    def validate_show_timing(self):
        if(
            self.show_start_time is not None
            and self.show_end_time is not None
            and self.show_start_time >= self.show_end_time
        ):
            raise ValidationError("show end time should be after than show start time")
        return self

class ShowResponse(BaseModel):
    model_config = ConfigDict(from_attributes = True)
    show_id : int
    movie_id: int
    screen_id : int

    show_start_time:datetime
    show_end_time:datetime

    show_format:str
    show_status:ShowStatus
    show_language:str


class ShowListFilters(BaseModel):
    movie_id : int = Field(default=None, gt=0)
    show_id : int = Field(default = None, gt = 0)

    start_from : datetime
    show_at : datetime

    show_format : str
    show_language: str
    show_status:ShowStatus

    @model_validator(mode="after")
    def validate_filter_range(self):
        if (
            self.start_from is not None
            and self.start_to is not None
            and self.start_to < self.start_from
        ):
            raise ValueError("start_to must be after start_from")
        return self