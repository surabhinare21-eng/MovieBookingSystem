import getpass

from sqlalchemy import select

from database import engine
from backend.app.core.security import hash_password
from backend.app.db.base import Base
from backend.app.db.session import SessionLocal
from backend.app.models.theatre import Theatre  
from backend.app.models.user import Role, User


def main():
    Base.metadata.create_all(bind=engine)

    username = input("Super admin username: ").strip()
    email = input("Super admin email: ").strip().lower()
    phone = input("Phone: ").strip()
    password = getpass.getpass("Password: ")

    db = SessionLocal()
    try:
        if db.scalar(select(User).where(User.user_email == email)):
            print("A user with this email already exists.")
            return

        db.add(User(
            username=username,
            user_email=email,
            phone_no=phone,
            hashed_password=hash_password(password),
            role=Role.SUPER_ADMIN.value,
        ))
        db.commit()
        print("Super admin created.")
    finally:
        db.close()


if __name__ == "__main__":
    main()