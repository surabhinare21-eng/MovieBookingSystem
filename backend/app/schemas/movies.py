from pydantic import BaseModel, ConfigDict, Field
from backend.app.models.show_enums import ShowLanguages
from datetime import time

class MovieCreate(BaseModel):
    movie_title: str = Field(min_length=1, max_length=255)
    movie_description: str = Field(min_length=1, max_length=255)
    movie_status: str = Field(min_length=1, max_length=100)
    movie_language: ShowLanguages
    movie_poster_url: str = Field(min_length=1, max_length=50)
    movie_rating: int = Field(ge=0, le=10)
    movie_duration:time = Field(gt=0)


class MovieUpdate(BaseModel):
    movie_title: str | None = Field(default=None, min_length=1, max_length=255)
    movie_description: str | None = Field(default=None, min_length=1, max_length=255)
    movie_status: str | None = Field(default=None, min_length=1, max_length=100)
    movie_language: ShowLanguages | None = None
    movie_poster_url: str | None = Field(default=None, min_length=1, max_length=50)
    movie_rating: int | None = Field(default=None, ge=0, le=10)
    movie_duration : time = Field(gt=0)


class MovieOut(BaseModel):
    movie_id: int
    movie_title: str
    movie_description: str
    movie_status: str
    movie_language: ShowLanguages
    movie_poster_url: str
    movie_rating: int
    movie_duration:time

    model_config = ConfigDict(from_attributes=True)
