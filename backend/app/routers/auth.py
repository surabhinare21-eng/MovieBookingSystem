from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.services.auth_service import login_user, register_customer

router = APIRouter(prefix="/auth", tags=["Authentication"])


class SignupRequest(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    user_email: EmailStr
    phone_no: str = Field(min_length=7, max_length=20)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    user_email: EmailStr
    password: str


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    try:
        user = register_customer(
            db=db,
            username=payload.username,
            email=str(payload.user_email),
            phone_no=payload.phone_no,
            password=payload.password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with these details already exists.",
        )

    return {
        "message": "Customer registered successfully.",
        "user": {
            "id": User.user_id,
            "username": User.username,
            "user_email": User.user_email,
            "role": User.role,
        },
    }


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        return login_user(
            db=db,
            email=str(payload.user_email),
            password=payload.password,
        )
    except ValueError as exc:
        if str(exc) == "This account has been deactivated.":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.user_id,
        "username": current_user.username,
        "user_email": current_user.user_email,
        "phone_no": current_user.phone_no,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
    }
