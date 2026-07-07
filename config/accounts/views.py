import email
from urllib import request

from django.shortcuts import render,redirect
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .utils import generate_otp, send_otp_email
from django.contrib.auth.models import User
import time
from .models import EmailOTP,Profile
from .services import resend_otp 

# Create your views here.
def register(request):
    if request.method=="POST":
        form=RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            otp_data = EmailOTP.objects.filter(
                email=email,
                purpose=EmailOTP.REGISTER
            ).first()

            if otp_data and not otp_data.is_expired():
                request.session["otp_email"] = email
                return redirect("accounts:verify_otp")
            
            otp = generate_otp()
            request.session['otp_email'] = email

            EmailOTP.objects.update_or_create(
                email=email,
                purpose=EmailOTP.REGISTER,
                defaults={
                    "username": username,
                    "password": password,
                    "otp": otp,
                    "resend_count": 0,
                }
            )

            send_otp_email(email, otp)
            return redirect('accounts:verify_otp')
    else:
        form=RegisterForm()
    return render(request,"accounts/register.html",{"form":form})

def logout_view(request):
    if request.method=="POST":
        logout(request)
        return render(request,"accounts/logout.html")
    return render(request,"accounts/confirm_logout.html")

def verify_otp(request):
    if request.method == "POST":
        email = request.session.get("otp_email")
        otp_data = EmailOTP.objects.filter(email=email,purpose=EmailOTP.REGISTER).first()
        if not otp_data:
            messages.error(request, "Session expired. Please register again.")
            return redirect('accounts:register')
        
        # Check if the OTP has expired (e.g., after 5 minutes)
        if otp_data.is_expired():
            messages.error(request, "OTP has expired. Please request a new one.")
            request.session.pop("otp_email", None)
            otp_data.delete()
            return redirect('accounts:register')

        if otp_data.otp == request.POST.get("otp"):
            # Create the user
            user = User.objects.create_user(
                username=otp_data.username,
                email=otp_data.email,
                password=otp_data.password
            )
            user.save()
            Profile.objects.create(
                user=user,
                role="Citizen"
            )
            # Clear the session & otp data
            request.session.pop("otp_email", None)
            otp_data.delete()

            messages.success(request, "Registration successful! You can now log in.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, "accounts/verify_otp.html")


def resend_register_otp(request):
    email = request.session.get("otp_email")

    success, message = resend_otp(email, EmailOTP.REGISTER)

    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    return redirect("accounts:verify_otp")

def resend_reset_otp(request):
    email = request.session.get("email_otp")

    success, message = resend_otp(email, EmailOTP.RESET)

    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    return redirect("accounts:verify_reset_otp")

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = generate_otp()
            request.session['email_otp'] = email
            EmailOTP.objects.update_or_create(
                email=email,
                purpose=EmailOTP.RESET,
                defaults={
                    "otp": otp,
                    "resend_count": 0,
                }
            )
            send_otp_email(email, otp)
            return redirect('accounts:verify_reset_otp')
        except User.DoesNotExist:
            messages.error(request, "No user found with this email.")
    return render(request, "accounts/forgot_password.html")

def verify_reset_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        email = request.session.get("email_otp")
        password_reset_data = EmailOTP.objects.filter(email=email).first()
        if not password_reset_data:
            messages.error(request, "Session expired. Please try again.")
            return redirect('accounts:forgot_password')
        
        # Check if the OTP has expired (e.g., after 5 minutes)
        if password_reset_data.is_expired(): 
            messages.error(request, "OTP has expired. Please request a new one.")
            request.session.pop("email_otp", None)
            password_reset_data.delete()
            return redirect('accounts:forgot_password')
        
        if entered_otp == password_reset_data.otp:
            password_reset_data.delete()
            request.session['otp_verified'] = True
            return redirect('accounts:reset_password')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, "accounts/verify_reset_otp.html")

def reset_password(request):
    if request.method == "POST":
        if not request.session.get('otp_verified') or request.session.get('email_otp') is None:
            messages.error(request, "You must verify the OTP before resetting your password.")
            return redirect('accounts:forgot_password')
        
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/reset_password.html")
        
        
        email=request.session.get("email_otp")
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        request.session.pop("email_otp", None)
        request.session.pop("otp_verified", None)

        messages.success(request, "Password reset successful! You can now log in.")
        return redirect('accounts:login')

    return render(request, "accounts/reset_password.html") 
