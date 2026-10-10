from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.core.security import(
    create_access_token,
    hash_password,
    verify_password,
)

from backend.app.models.user import User
from backend.app.models.user import Role

def register_customer(db, username, email, phone_no, password) -> User:
    """
    Register a new customer.

    Customers cannot choose their own role or theatre assignment.
    """
    normalized_email = email.strip().lower()

    # Check whether this email is already registered.
    existing_user = db.scalar(select(User).where(User.user_email == normalized_email))

    if existing_user:
        raise ValueError("An account with this email already exists.")

    # Customers always receive the CUSTOMER role.
    user = User(
        username=username.strip(),
        user_email=normalized_email,
        phone_no=phone_no.strip(),
        hashed_password=hash_password(password),
        role=Role.CUSTOMER,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def login_user(
    db: Session,
    email: str,
    password: str,
) -> dict:
    """Authenticate a user and return an access token."""

    normalized_email = email.strip().lower()

    user = db.scalar(
        select(User).where(User.user_email == normalized_email)
    )

    # Use the same message for an unknown email and a wrong password.
    if user is None or not verify_password(
        password,
        user.hashed_password,
    ):
        raise ValueError("Invalid email or password.")

    if not user.is_active:
        raise ValueError("This account has been deactivated.")

    access_token = create_access_token(
        user_id=User.user_id,
        role=user.role,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
