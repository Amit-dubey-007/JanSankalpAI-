from django.core.mail import send_mail
from django.conf import settings
import random

def generate_otp():
    return str(random.randint(100000, 999999))


# def send_otp_email(email, otp, purpose="Verification"):
#     subject = f"{purpose} OTP Code"
#     message = f"Your OTP is: {otp}\nDo not share it with anyone. It will expire in 5 minutes."

#     send_mail(
#         subject,
#         message,
#         settings.EMAIL_HOST_USER,
#         [email],
#         fail_silently=False
#     ) 

import requests

def send_otp_email(email, otp):
    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json",
        },
        json={
            "sender": {
                "name": "JanSankalpAI",
                "email": settings.EMAIL_HOST_USER,
            },
            "to": [
                {
                    "email": email
                }
            ],
            "subject": "Verify your Email",
            "htmlContent": f"""
                <h2>Email Verification</h2>
                <p>Your OTP is:</p>
                <h1>{otp}</h1>
                <p>This OTP expires in 10 minutes.</p>
            """,
        },
        timeout=15,
    )

    print(response.status_code)
    print(response.text)

    response.raise_for_status()