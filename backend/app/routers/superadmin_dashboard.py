from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.city import City
from backend.app.models.movies import Movie
from backend.app.models.screens import Screen
from backend.app.models.theatre import Theatre
from backend.app.models.user import User
from backend.app.services.admin_service import (
    get_city_coordinates,
    get_customer_admin_para,
    get_movies_list,
    get_theater_admin_list,
    get_theater_customer_list,
    get_theaters_list,
    graphs_screen_theater,
    graphs_theater_city,
)
from backend.app.services.admin_service import (
    get_total_analytics_count_superadmin as gtacs,
)

router = APIRouter(prefix="/get_analytics", tags=["Root Admin (SUPER_ADMIN)"])

@router.get("/superadmin")
def get_admin_analytics(db = Depends(get_db)):
    return gtacs(db, Users=User, Theatres=Theatre, Cities=City, Movie=Movie)
    
@router.get("/map_data")
def city_mapping(db = Depends(get_db)):
    return get_city_coordinates(db=db, Cities=City)

@router.get("/graphical_theater_city")
def graph_theater_city(db = Depends(get_db)):
    return graphs_theater_city(db, Theatre, City)

@router.get("/graphical_screen_theater")
def graph_screen_theater(db = Depends(get_db)):
    return graphs_screen_theater(db, Screen, Theatre)

@router.get("/get_movies_list")
def get_movies_names(db=Depends(get_db)):
    return get_movies_list(db, Movie)

@router.get("/get_theater_list")
def get_theaters_names(db=Depends(get_db)):
    return get_theaters_list(db, Theatre)

@router.get("/theater_admin_list")
def get_theater_list(db = Depends(get_db)):
    return get_theater_admin_list(db, User)

@router.get("/get_customer_list")
def get_customer_list(db = Depends(get_db)):
    return get_theater_customer_list(db, User)

@router.get("/get_para_line_graph")
def get_customer_admin(db = Depends(get_db)):
    return get_customer_admin_para(db, User)