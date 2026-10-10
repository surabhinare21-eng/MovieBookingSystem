from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.models.user import User

from app.db.session import get_db

db = get_db()
def get_user_by_email(db, email):
    return db.scalar(select(User).where(User.user_email == email.lower()))

def get_user_by_role(db, role):
    return db.scalar(select(User).where(User.role == role.upper()))

def create_user(db, user_in, hashed_password):
    user = User(
        username=user_in.username,
        user_email = user_in.user_email,
        phone_no = user_in.phone_no,
        hashed_password = user_in.hashed_password,
        role = user_in.role
    )    
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(db, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_users(db, skip, limit):
    return list(db.scalars(select(User).offset(skip).limit(limit)))


def update_user(db, user, data):
    for field, value in data.items():
        setattr(user, field, value)
        
    db.commit()
    db.refresh(user)
    
    return user

def delete_user(db, user) -> None:
    db.delete(user)
    db.commit()
    