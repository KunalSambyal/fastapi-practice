import asyncio
from email.message import EmailMessage
import os
import secrets
import smtplib
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)


def generate_otp() -> str:
    """Generate a secure random 6-digit numeric OTP"""

    return str(secrets.randbelow(900000) + 100000)


def _send_sync_email(to_email: str, otp_code: str):
    """Synchronous SMTP email delivery."""

    msg = EmailMessage()
    msg["Subject"] = "Password Reset OTP Code"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.set_content(
        f"Hello,\n\n"
        f"Your one-time password (OTP) for resetting your password is: {otp_code}\n\n"
        f"This code will expire in 10 minutes.\n"
        f"If you did not request a password reset, please ignore this email."
    )
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

async def send_otp_email(to_email: str, otp_code: str) -> None:
    """Async wrapper so email sending dosen't block the FastAPI event loop."""
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
        print(f"\n============================")
        print(f"[DEV MODE] OTP for {to_email}: {otp_code}")
        print(f"\n============================")
        return

    await asyncio.to_thread(_send_sync_email, to_email, otp_code)