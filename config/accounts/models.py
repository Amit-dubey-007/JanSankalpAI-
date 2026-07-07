from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class EmailOTP(models.Model):
    REGISTER = "register"
    RESET = "reset"

    PURPOSE_CHOICES = [
        (REGISTER, "Register"),
        (RESET, "Reset Password"),
    ]
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now=True)
    resend_count = models.IntegerField(default=0)
    last_resend_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email} - {self.otp}"
    
    def is_expired(self):
        expiration_time = self.created_at + timezone.timedelta(minutes=5)
        return timezone.now() > expiration_time
    
    def can_resend(self):
        if self.last_resend_time + timezone.timedelta(seconds=30) > timezone.now():
            return False
        return True
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email", "purpose"],
                name="unique_email_purpose"
            )
        ]
    
class Profile(models.Model):
    ROLE_CHOICES = [
        ("Citizen", "Citizen"),
        ("Government", "Government"),
        ("Admin","Admin"),
    ]

    LANGUAGE_CHOICES = [
        ("English", "English"),
        ("Hindi", "Hindi"),
        ("Marathi", "Marathi"),
        ("Gujarati", "Gujarati"),
        ("Bengali", "Bengali"),
        ("Tamil", "Tamil"),
        ("Telugu", "Telugu"),
        ("Kannada", "Kannada"),
        ("Malayalam", "Malayalam"),
        ("Punjabi", "Punjabi"),
        ("Odia", "Odia"),
        ("Assamese", "Assamese"),
        ("Maithili", "Maithili"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Identity
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="Citizen")

    # Metadata
    joined_at = models.DateTimeField(auto_now_add=True)

    # ------------------- all add later ----------------------

    # phone = models.CharField(max_length=15, blank=True)

    # Location
    # state = models.CharField(max_length=100, blank=True)
    # district = models.CharField(max_length=100, blank=True)
    # address = models.TextField(blank=True, max_length=200)

    # Preferences
    # preferred_language = models.CharField(max_length=30, choices=LANGUAGE_CHOICES, default="English")

    # Verification
    # is_verified = models.BooleanField(default=False)

    # Anti-spam / Moderation (add later)
    # reputation_score = models.PositiveSmallIntegerField(default=100)

    # invalid_reports = models.PositiveIntegerField(default=0)

    # warning_count = models.PositiveIntegerField(default=0)

    # is_temporarily_blocked = models.BooleanField(default=False)

    # blocked_until = models.DateTimeField(blank=True, null=True)

    # Complaint cooldown
    # last_complaint_at = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return self.user.username