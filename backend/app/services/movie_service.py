from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.models.movies import Movie
from backend.app.schemas.movies import MovieCreate, MovieUpdate



def create_movie(db: Session, payload: MovieCreate):
    movie = Movie(**payload.model_dump())

    db.add(movie)
    db.commit()
    db.refresh(movie)

    return movie


def get_all_movies(db: Session):
    return list(db.scalars(select(Movie).order_by(Movie.movie_id)).all())


def get_movie_by_id(db: Session, movie_id: int):
    return db.scalar(select(Movie).where(Movie.movie_id == movie_id))


def update_movie(
    db: Session,
    movie_id: int,
    payload: MovieUpdate
):
    movie = get_movie_by_id(db, movie_id)

    if not movie:
        return None
    #  only the keys which was explicitly passed while instantiating the model will only be passed in hte dctionary
    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(movie, key, value)

    db.commit()
    db.refresh(movie)

    return movie


def delete_movie(db: Session, movie_id: int):
    movie = get_movie_by_id(db, movie_id)

    if not movie:
        return False

    db.delete(movie)
    db.commit()

    return True
