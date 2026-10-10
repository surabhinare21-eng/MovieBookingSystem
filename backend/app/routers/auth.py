from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserLogin
from backend.app.services.auth_service import login_user, register_customer

router = APIRouter(prefix="/auth", tags=["Authentication"])

# @router.post("/signup", status_code=status.HTTP_201_CREATED)
# async def signup(
#     request: Request,
#     db: Session = Depends(get_db),
# ):
#     """Register a new customer."""

#     try:
#         data = await request.json()
#     except (ValueError, UnicodeDecodeError):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Request body must contain valid JSON.",
#         )

#     if not isinstance(data, dict):
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="Request body must be a JSON object.",
#         )

#     full_name = get_required_text(data, "full_name")
#     email = get_required_text(data, "email")
#     password = data.get("password")

#     if not isinstance(password, str) or not password:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="'password' is required.",
#         )

#     if len(full_name) > 100:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="Full name must not exceed 100 characters.",
#         )

#     if len(email) > 255 or "@" not in email:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="Enter a valid email address.",
#         )

#     if len(password) < 8:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="Password must contain at least 8 characters.",
#         )

#     try:
#         user = register_customer(
#             db=db,
#             full_name=full_name,
#             email=email,
#             password=password,
#         )
#     except ValueError as exc:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=str(exc),
#         )

#     return {
#         "message": "Customer registered successfully.",
#         "user": {
#             "id": user.id,
#             "full_name": user.full_name,
#             "email": user.email,
#             "role": user.role.value,
#         },
#     }

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    try:
        user = register_customer(
            db=db,
            username=payload.username,
            email=str(payload.user_email),
            phone_no=payload.phone_no,
            password=payload.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with these details already exists.",
        ) from None

    return {
        "message": "Customer registered successfully.",
        "user": {
            "id": user.user_id,
            "username": user.username,
            "user_email": user.user_email,
            "role": user.role.value,
        },
    }

# @router.post("/login")
# async def login(
#     request: Request,
#     db: Session = Depends(get_db),
# ):
#     """Authenticate a user and return a JWT."""

#     try:
#         data = await request.json()
#     except (ValueError, UnicodeDecodeError):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Request body must contain valid JSON.",
#         )

#     if not isinstance(data, dict):
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="Request body must be a JSON object.",
#         )

#     email = get_required_text(data, "email")
#     password = data.get("password")

#     if not isinstance(password, str) or not password:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="'password' is required.",
#         )

#     try:
#         return login_user(
#             db=db,
#             email=email,
#             password=password,
#         )
#     except ValueError as exc:
#         message = str(exc)

#         if message == "This account has been deactivated.":
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=message,
#             )

#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password.",
#             headers={"WWW-Authenticate": "Bearer"},
#         )


@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    try:
        return login_user(
            db=db,
            email=str(payload.user_email),
            password=payload.password,
        )
    except ValueError as exc:
        if str(exc) == "This account has been deactivated.":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(exc),
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


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


from fastapi import APIRouter,Depends,HTTPException,Request,status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.auth_service import(login_user,register_customer)

router = APIRouter(prefix="/auth",tags=["Authentication"])

def get_required_text(data: dict, field: str) -> str:
    """Retrieve a required, non-empty string from a request body."""

    value = data.get(field)

    if not isinstance(value, str) or not value.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"'{field}' is required and must be a non-empty string.",
        )

    return value.strip()






@router.get("/me")
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    """Return the profile of the currently authenticated user."""

    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role.value,
        "theatre_id": current_user.theatre_id,
        "is_active": current_user.is_active,
    }