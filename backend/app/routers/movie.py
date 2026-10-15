from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session 


from backend.app.core.permissions import require_roles
from backend.app.db.session import get_db
from backend.app.models.user import Role
from backend.app.schemas.movies import MovieCreate, MovieOut, MovieUpdate
from backend.app.services import movie_service


router = APIRouter(prefix="/movies", tags=["Movies"])
super_admin_only = require_roles(Role.SUPER_ADMIN)


@router.post(
    "/",
    response_model=MovieOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(super_admin_only)],
)
def create_movie(payload: MovieCreate, db: Session = Depends(get_db)):
    try:
        return movie_service.create_movie(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

@router.get("/", response_model=list[MovieOut])
def get_all_movies(db: Session = Depends(get_db)):
    return movie_service.get_all_movies(db)


@router.get("/{movie_id}", response_model=MovieOut)
def get_movie_by_id(movie_id: int, db: Session = Depends(get_db)):
    movie = movie_service.get_movie_by_id(db, movie_id)
    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found.",
        )
    return movie


@router.patch(
    "/{movie_id}",
    response_model=MovieOut,
    dependencies=[Depends(super_admin_only)],
)
def update_movie(
    movie_id: int, payload: MovieUpdate,
    db: Session = Depends(get_db),
):
    movie = movie_service.update_movie(db, movie_id, payload)
    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found.",
        )
    return movie


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(super_admin_only)],
)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    if not movie_service.delete_movie(db, movie_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
