from sqlalchemy import select

from backend.app.core.security import hash_password
from backend.app.models.theatre import Theatre
from backend.app.models.city import City
from backend.app.models.user import Role, User


def create_city(db, name) -> City:
    exists = db.scalar(
        select(City).where(City.name == name.strip())
    )
    if exists:
        raise ValueError("A City with this name already exists.")

    city = City(name=name.strip(), city=city.strip())
    db.add(city)
    db.commit()
    db.refresh(city)
    return City

def set_city_active(db,name,city_id:int,is_active:bool)-> City:
    city = db.get(City,city_id)
    if city is None:
        raise LookupError("City not found")
    
    city.is_active = is_active
    db.commit()
    db.refresh(city)
    return city


def create_theatre(db, name, city, address) -> Theatre:
    exists = db.scalar(
        select(Theatre).where(Theatre.name == name.strip(), Theatre.city == city.strip())
    )
    if exists:
        raise ValueError("A theatre with this name already exists in this city.")

    theatre = Theatre(name=name.strip(), city=city.strip(), address=address.strip())
    db.add(theatre)
    db.commit()
    db.refresh(theatre)
    return theatre

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