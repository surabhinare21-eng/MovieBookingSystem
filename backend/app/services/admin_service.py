from sqlalchemy import select, func, Date, case

from backend.app.core.security import hash_password
from backend.app.models.theatre import Theatre
from backend.app.models.city import City
from backend.app.models.user import Role, User
from backend.app.db.session import get_db
from geopy.geocoders import Nominatim   
from geopy.exc import GeocoderServiceError
import json

def create_city(db, name: str) -> City:
    # 1. Standardize the name input first
    clean_name = name.strip()

    # 2. Check for existence in the database
    exists = db.scalar(select(City).where(City.name == clean_name))
    if exists:
        raise ValueError("A City with this name already exists.")

    # 3. Initialize Nominatim
    geolocator = Nominatim(user_agent="my_geocoder_app")

    try:
        # 4. Attempt to find the coordinates
        city_coordinates = geolocator.geocode(clean_name)

        if not city_coordinates:
            raise ValueError(
                f"Could not find coordinates for the city: {clean_name}"
            )

        # 5. Correctly instantiate the SQLAlchemy model using keyword arguments
        city = City(
            name=clean_name,
            longitude=city_coordinates.longitude,
            latitude=city_coordinates.latitude,
        )

        db.add(city)
        db.commit()
        db.refresh(city)
        return city

    except GeocoderServiceError:
        db.rollback()  # Rollback if an error happens during the process
        raise RuntimeError("Geocoding service is temporarily unavailable.")

def set_city_active(db,name,city_id:int,is_active:bool)-> City:
    city = db.get(City,city_id)
    if city is None:
        raise LookupError("City not found")
    
    city.is_active = is_active
    db.commit()
    db.refresh(city)
    return city


def create_theatre(db, name, city, address) -> Theatre:
    city_record = db.scalar(
        select(City).where(City.name == city.strip(), City.is_active.is_(True))
    )
    if city_record is None:
        raise LookupError("City not found or inactive.")

    exists = db.scalar(
        select(Theatre).where(
            Theatre.name == name.strip(),
            Theatre.city_id == city_record.city_id,
        )
    )
    if exists:
        raise ValueError("A theatre with this name already exists in this city.")

    theatre = Theatre(
        name=name.strip(),
        city_id=city_record.city_id,
        address=address.strip(),
        contact_info="",
    )
    db.add(theatre)
    db.commit()
    db.refresh(theatre)
    return theatre


def update_theatre(db, theatre_id, name, city, address) -> Theatre:
    # 1. Find the existing theatre
    theatre = db.get(Theatre, theatre_id)

    if theatre is None:
        raise LookupError("Theatre not found.")

    # 2. Validate the city
    city_record = db.scalar(
        select(City).where(
            City.name == city.strip(),
            City.is_active.is_(True)
        )
    )

    if city_record is None:
        raise LookupError("City not found or inactive.")

    # 3. Check for duplicate theatre name in the same city
    exists = db.scalar(
        select(Theatre).where(
            Theatre.name == name.strip(),
            Theatre.city_id == city_record.city_id,
            Theatre.theatre_id != theatre_id
        )
    )

    if exists:
        raise ValueError(
            "A theatre with this name already exists in this city."
        )

    # 4. Update the theatre fields
    theatre.name = name.strip()
    theatre.city_id = city_record.city_id
    theatre.address = address.strip()

    # 5. Save changes
    db.commit()
    db.refresh(theatre)

    return theatre

def get_theatres_by_city(db, city_id: int):
    city = db.get(City, city_id)

    if city is None or not city.is_active:
        return []

    return db.scalars(
        select(Theatre).where(
            Theatre.city_id == city_id,
            Theatre.is_active.is_(True),
        )
    ).all()

def set_theatre_active(db, theatre_id: int, is_active: bool) -> Theatre:
    theatre = db.get(Theatre, theatre_id)
    if theatre is None:
        raise LookupError("Theatre not found.")

    theatre.is_active = is_active
    db.commit()
    db.refresh(theatre)
    return theatre


def create_theatre_admin(db, username, email, phone_no, password, theatre_id) -> User:
    if db.get(Theatre, theatre_id) is None:
        raise LookupError("Theatre not found.")

    normalized_email = email.strip().lower()
    if db.scalar(select(User).where(User.user_email == normalized_email)):
        raise ValueError("An account with this email already exists.")

    user = User(
        username=username.strip(),
        user_email=normalized_email,
        phone_no=phone_no.strip(),
        hashed_password=hash_password(password),
        role=Role.ADMIN.value,
        theatre_id=theatre_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def delete_theatre(db, theatre_id):
    theatre = db.get(Theatre, theatre_id)

    if theatre is None:
        raise LookupError("Theatre not found.")

    db.delete(theatre)
    db.commit()

    return {"message": "Theatre deleted successfully."}

def set_user_active(db, user_id: int, is_active: bool, acting_user: User) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise LookupError("User not found.")
    if user.user_id == acting_user.user_id:
        raise ValueError("You cannot block or unblock your own account.")
    if user.role == Role.SUPER_ADMIN.value:
        raise ValueError("Super admin accounts cannot be blocked.")

    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user

def get_total_analytics_count_superadmin(db, Users, Theatres, Cities, Movie):
    statement_total_users = select(func.count(Users.user_id)).where(Users.role == "CUSTOMER")
    total_customers = db.scalar(statement_total_users)
    
    statement_theater_admin = select(func.count(Users.user_id)).where(Users.role == "ADMIN")
    total_theater_admin = db.scalar(statement_theater_admin)
    
    statement_total_theater = select(func.count(Theatres.theatre_id))
    total_theater = db.scalar(statement_total_theater)
    
    statement_total_cities = select(func.count(Cities.city_id))
    total_cities = db.scalar(statement_total_cities)

    statement_total_movies = select(func.count(Movie.movie_id))
    total_movies = db.scalar(statement_total_movies)
        
    return {
        "total_customers_count": total_customers,
        "total_theater_admin_count": total_theater_admin,
        "total_theater_count": total_theater,
        "total_cities": total_cities,
        "total_movies": total_movies
    }

def get_city_coordinates(db, Cities):
  statement_city_coordinates = select(Cities.longitude, Cities.latitude)
  city_coordinates = db.execute(statement_city_coordinates).mappings().all()
  
  
  return [dict(row) for row in city_coordinates]
  
def graphs_theater_city(db, Theatre, Cities):
    results = (
    db.query(Cities.name, func.count(Theatre.theatre_id).label("theatre_count"))
    .join(Theatre, Cities.city_id == Theatre.city_id)
    .group_by(Cities.name)
    .all()
    )
    
    analytics_payload = {row.name: row.theatre_count for row in results}
    
    return analytics_payload

def graphs_screen_theater(db, Screen, Theatre):
    results = (
        db.query(Theatre.name, func.count(Screen.screen_id).label("screen_count"))
        .join(Screen, Theatre.theatre_id == Screen.theatre_id) 
        .group_by(Theatre.name)
        .all()
    )
    
    analytics_payload = {row.name: row.screen_count for row in results}
    return analytics_payload

def get_movies_list(db, Movie):
    statement_movies_list = select(Movie.movie_title)
    movie_names = db.execute(statement_movies_list).scalars().all()
    
    return movie_names

def get_theaters_list(db, Theatre):
    statement_theater_list = select(Theatre.name)
    theater_list = db.execute(statement_theater_list).scalars().all()
    
    return theater_list

def get_theater_admin_list(db, User):
    statement_theater_admin_list = select(User.username, User.user_email, User.phone_no).where(User.role == "ADMIN")
    theater_admin_list = db.execute(statement_theater_admin_list).all()
    
    theater_admin_info = [
        {"admin_name":admin_name, "email":email, "phone_no":phone_no}
        for admin_name, email, phone_no in theater_admin_list
    ]
    
    return theater_admin_info

def get_theater_customer_list(db, User):
    statement_theater_admin_list = select(User.username, User.user_email, User.phone_no).where(User.role == "CUSTOMER")
    customer_list = db.execute(statement_theater_admin_list).all()
    
    theater_admin_info = [
        {"customer_name":cust_name, "email":email, "phone_no":phone_no}
        for cust_name, email, phone_no in customer_list
    ]
    
    return theater_admin_info

def get_customer_admin_para(db, User):
    date_label = func.cast(User.created_at, Date).label("date")

    statement = (
        select(
            date_label,
            func.count(case((User.role == "ADMIN", 1))).label("Admins"),
            func.count(case((User.role == "CUSTOMER", 1))).label("Customers"),
        )
        .group_by(date_label)
        .order_by(date_label.asc())
    )

    results = db.execute(statement).mappings().all()
    return [
        {
            "date": str(row["date"]),
            "Admins": int(row["Admins"] or 0),
            "Customers": int(row["Customers"] or 0),
        }
        for row in results
    ]
    
def get_superadmin_total_movies(db, Movie):
    statement = select(func.count(Movie.movie_title))
    movie_titles_count = db.scalar(statement)
    
    return movie_titles_count

def get_superadmin_total_screens(admin_id, db, Screen):
    statement = select(func.count(Screen.screen_id)).where(Screen.theatre_id == admin_id)
    screen_count = db.scalar(statement)
    
    return screen_count if screen_count is not None else 0

def get_superadmin_total_shows(admin_id, db, Screen, Shows):
    screen_statement = select(Screen.screen_id).where(Screen.theatre_id == admin_id)
    screen_ids = db.scalars(screen_statement).all()
    
    if not screen_ids:
        return 0
    
    show_statement = select(func.count(Shows.show_id)).where(Shows.screen_id.in_(screen_ids))
    show_count = db.scalar(show_statement)
    
    return show_count if show_count else 0

def get_theatre_name_admin(admin_id, db, Theatre):
    theatre_statement = select(Theatre.name).where(Theatre.theatre_id == admin_id)
    theatre_name = db.scalar(theatre_statement)
    
    return theatre_name


def get_city_name_admin(admin_id, db, Theatre, City):
    statement = (
        select(City.name)
        .select_from(Theatre)
        .join(City, Theatre.city_id == City.city_id)
        .where(Theatre.theatre_id == admin_id)
    )

    city_name = db.scalar(statement)
    return city_name if city_name else "Unknown City"

def get_city_list_admin(db, City):
    statement = select(City.name)
    city_list = db.scalars(statement).all()
    
    return city_list if city_list else "No added cities"

def get_screen_list(admin_id, db, Screen):
    statement = select(Screen.screen_name).where(Screen.theatre_id == admin_id)
    screen_list = db.scalar(statement)
    
    return screen_list if screen_list else "No screen added"

