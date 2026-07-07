from django.core.mail import send_mail
from django.conf import settings
import random

def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp, purpose="Verification"):
    subject = f"{purpose} OTP Code"
    message = f"Your OTP is: {otp}\nDo not share it with anyone. It will expire in 5 minutes."

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False
    ) 