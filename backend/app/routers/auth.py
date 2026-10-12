from datetime import datetime, timedelta
import smtplib
import logging 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user
from backend.app.core.security import hash_password
from backend.app.db.session import get_db
from backend.app.models.pending_registration import PendingRegistration
from backend.app.models.user import Role, User
from backend.app.schemas.user import EmailVerification, UserCreate, UserLogin
from backend.app.services.auth_service import login_user
from backend.app.services.email_verification import generate_otp, hash_otp, send_verification_otp

router = APIRouter(prefix="/auth", tags=["Authentication"])
OTP_TTL_MINUTES = 10
MAX_OTP_ATTEMPTS = 5


logger=logging.getLogger(__name__)



@router.post("/signup/request-verification", status_code=status.HTTP_200_OK)
def request_signup_verification(payload: UserCreate, db: Session = Depends(get_db)):
    """Send an OTP. The users table is not touched until OTP verification succeeds."""
    normalized_email = str(payload.user_email).strip().lower()

    existing_user = db.scalar(select(User).where(User.user_email == normalized_email))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists. Please log in.",
        )

    # Replace any previous pending attempt for this email.
    previous = db.scalar(
        select(PendingRegistration).where(PendingRegistration.user_email == normalized_email)
    )
    if previous:
        db.delete(previous)
        db.flush()

    otp = generate_otp()
    pending = PendingRegistration(
        username=payload.username.strip(),
        user_email=normalized_email,
        phone_no=payload.phone_no.strip(),
        hashed_password=hash_password(payload.password),
        otp_hash=hash_otp(otp),
        expires_at=datetime.utcnow() + timedelta(minutes=OTP_TTL_MINUTES),
        attempts=0,
    )
    db.add(pending)
    db.commit()

    try:
        send_verification_otp(normalized_email, otp)
    except (OSError, smtplib.SMTPException, RuntimeError) as exc:
        logger.exception("Failed to send signup verification email")
        
        db.delete(pending)
        db.commit()
        # Do not expose SMTP credentials or internal exception details to clients.
        
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "We could not send a verification email. Check the email address and try again. "
                "If the problem continues, contact support."
            ),
        ) from exc

    return {"message": "Verification code sent. Check your email and enter the 6-digit code."}


@router.post("/signup/verify", status_code=status.HTTP_201_CREATED)
def verify_signup_email(payload: EmailVerification, db: Session = Depends(get_db)):
    normalized_email = str(payload.user_email).strip().lower()
    pending = db.scalar(
        select(PendingRegistration).where(PendingRegistration.user_email == normalized_email)
    )

    if pending is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending registration found. Please sign up and request a new code.",
        )

    if pending.expires_at < datetime.utcnow():
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The verification code has expired. Please sign up again to receive a new code.",
        )

    if pending.attempts >= MAX_OTP_ATTEMPTS:
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many incorrect attempts. Please sign up again to request a new code.",
        )

    if hash_otp(payload.otp) != pending.otp_hash:
        pending.attempts += 1
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect verification code. Please check the email and try again.",
        )

    # Only now create the permanent user record.
    existing_user = db.scalar(select(User).where(User.user_email == normalized_email))
    if existing_user:
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists. Please log in.",
        )

    user = User(
        username=pending.username,
        user_email=pending.user_email,
        phone_no=pending.phone_no,
        hashed_password=pending.hashed_password,
        role=Role.CUSTOMER.value,
    )
    try:
        db.add(user)
        db.flush()
        db.delete(pending)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists. Please log in.",
        ) from None

    return {
        "message": "Email verified and account created successfully. You can now log in.",
        "user": {
            "id": user.user_id,
            "username": user.username,
            "user_email": user.user_email,
            "role": user.role,
        },
    }


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
        "role": current_user.role,
        "is_active": current_user.is_active,
    }




