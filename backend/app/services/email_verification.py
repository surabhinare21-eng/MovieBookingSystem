import hashlib
import os
import secrets
import smtplib
from email.message import EmailMessage


OTP_LENGTH = 6


def generate_otp() -> str:
    return f"{secrets.randbelow(10 ** OTP_LENGTH):0{OTP_LENGTH}d}"


def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()


def send_verification_otp(recipient: str, otp: str) -> None:
    """Send an email verification code using Gmail SMTP SSL."""
    gmail_address = os.getenv("GMAIL_ADDRESS", "").strip()
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD", "").replace(" ", "")

    if not gmail_address or not gmail_app_password:
        raise RuntimeError(
            "Gmail is not configured. Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env."
        )

    message = EmailMessage()
    message["Subject"] = "Movie Booking System - Verify your email"
    message["From"] = gmail_address
    message["To"] = recipient
    message.set_content(
        "Hello,\n\n"
        f"Your Movie Booking System email verification code is: {otp}\n\n"
        "This code expires in 10 minutes. If you did not request this, you can ignore this email.\n"
    )

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.set_debuglevel(1)
        smtp.login(gmail_address, gmail_app_password)
        smtp.send_message(message)
