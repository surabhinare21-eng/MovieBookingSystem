from fastapi import APIRouter, Depends
from backend.app.db.session import get_db

from backend.app.models.movies import Movie
from backend.app.models.screens import Screen
from backend.app.models.shows import Show
from backend.app.models.theatre import Theatre
from backend.app.models.city import City
from backend.app.models.booking import Booking
from backend.app.models.user import User

from backend.app.services.admin_service import (
    get_superadmin_total_movies,
    get_superadmin_total_screens,
    get_superadmin_total_shows,
    get_theatre_name_admin,
    get_city_name_admin,
    get_city_list_admin,
    get_screen_list,
    get_top_movies_list,
    get_shows_sold_per_movie,
)

router = APIRouter(prefix="/get_analytics_theatreadmin", tags=["Theatre Admin (ADMIN)"])

@router.get("/total_movies")
def get_total_movies(db = Depends(get_db)):
    return get_superadmin_total_movies(db, Movie)
    
@router.get("/total_screens")
def get_total_screens(admin_id: int, db = Depends(get_db)):
    return get_superadmin_total_screens(admin_id, db, Screen)

@router.get("/total_shows")
def get_total_shows(admin_id: int, db = Depends(get_db)):
    return get_superadmin_total_shows(admin_id, db, Screen, Show)
    
@router.get("/theatre_name")
def get_theatre_name(admin_id: int, db = Depends(get_db)):
    return get_theatre_name_admin(admin_id, db, Theatre)

@router.get("/city_name")
def get_city_name(admin_id: int, db = Depends(get_db)):
    return get_city_name_admin(admin_id, db, Theatre, City)

@router.get("/get_cities_list")
def get_city_list(db = Depends(get_db)):
    return get_city_list_admin(db, City)

@router.get("/get_screens_list")
def get_screen_list_admin(admin_id, db = Depends(get_db)):
    return get_screen_list(admin_id, db, Screen)

@router.get("/get_top_movies")
def get_top_movies(admin_id, db = Depends(get_db)):
    return get_top_movies_list(admin_id, db, Movie, Booking, Show, Screen, Theatre)

@router.get("/get_shows_sold")
def get_shows_sold(admin_id, db = Depends(get_db)):
    return get_shows_sold_per_movie(admin_id, db, Movie, Show, Booking, Screen, Theatre, User)