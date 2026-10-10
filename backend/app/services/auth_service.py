from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import(
    create_access_token,
    hash_password,
    verify_password,
)

from app.models.user import User

def register_customer(db,username,email,password) -> User:
    """
    Register a new customer.

    Customers cannot choose their own role or theatre assignment.
    """
    normalized_email = email.strip().lower()

    # Check whether this email is already registered.
    existing_user = db.scalar(
        select(User).where(User.email == normalized_email)
    )

    if existing_user:
        raise ValueError("An account with this email already exists.")

    # Customers always receive the CUSTOMER role.
    user = User(
        full_name=usernamename.strip(),
        email=normalized_email,
        password_hash=hash_password(password),
        role=UserRole.CUSTOMER,
        theatre_id=None,
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
        select(User).where(User.email == normalized_email)
    )

    # Use the same message for an unknown email and a wrong password.
    if user is None or not verify_password(
        password,
        user.password_hash,
    ):
        raise ValueError("Invalid email or password.")

    if not user.is_active:
        raise ValueError("This account has been deactivated.")

    access_token = create_access_token(
        user_id=user.id,
        role=user.role.value,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

