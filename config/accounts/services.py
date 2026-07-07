from django.utils import timezone
import time
from accounts.models import EmailOTP
from accounts.utils import generate_otp, send_otp_email
from django.db.models import F

def resend_otp(email, purpose):
    otp_data = EmailOTP.objects.filter(
        email=email,
        purpose=purpose
    ).first()

    if not otp_data:
        return False, "OTP request not found."

    if otp_data.resend_count >= 3:
        otp_data.delete()
        return False, "Maximum resend attempts reached. Please start again."
    
    if not otp_data.can_resend():
        return False, "Please wait before requesting another OTP."

    otp_data.resend_count = F('resend_count') + 1

    otp = generate_otp()

    otp_data.otp = otp
    otp_data.save()   # auto_now updates timestamps

    send_otp_email(email, otp)

    return True, "A new OTP has been sent to your email."