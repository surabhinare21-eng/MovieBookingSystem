import os
import smtplib
from email.message import EmailMessage


def send_booking_confirmation(
    recipient: str,
    booking_id: int,
    movie_name: str,
    theatre_name: str,
    screen_name: str,
    seat_labels: list[str],
    amount: str,
) -> None:
    """Send a booking confirmation using the existing Gmail configuration."""
    gmail_address = os.getenv("GMAIL_ADDRESS", "").strip()
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD", "").replace(" ", "")

    if not gmail_address or not gmail_app_password:
        raise RuntimeError("Gmail is not configured for booking confirmation email.")

    message = EmailMessage()
    message["Subject"] = f"Movie Booking System - Booking confirmed #{booking_id}"
    message["From"] = gmail_address
    message["To"] = recipient
    message.set_content(
        "Hello,\n\nYour payment was successful and your movie booking is confirmed.\n\n"
        f"Booking ID: {booking_id}\n"
        f"Movie: {movie_name}\n"
        f"Theatre: {theatre_name}\n"
        f"Screen: {screen_name}\n"
        f"Seats: {', '.join(seat_labels) if seat_labels else 'Please check your booking details'}\n"
        f"Amount paid: ₹{amount}\n\n"
        "Thank you for booking with Movie Booking System!\n"
    )

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(gmail_address, gmail_app_password)
        smtp.send_message(message)
