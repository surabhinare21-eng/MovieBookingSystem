from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ShowCreate(BaseModel):
    show_start_time: datetime
    show_end_time: datetime
    show_status: bool = True
    show_language: str
    show_format: str
    screen_id: int
    movie_id: int

class ShowUpdate(BaseModel):
    show_start_time: datetime 
    show_end_time: datetime  
    show_status: bool  
    show_language: str 
    show_format: str  
    screen_id: int  
    movie_id: int 
class ShowOut(BaseModel):
    show_id: int
    show_start_time: datetime
    show_end_time: datetime
    show_status: bool
    show_language: str
    show_format: str
    screen_id: int
    movie_id: int

    
    model_config = ConfigDict(from_attributes=True)


class ShowStatus(BaseModel):
    show_status: bool
