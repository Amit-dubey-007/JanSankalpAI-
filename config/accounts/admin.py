from django.contrib import admin
from .models import EmailOTP,Profile
# Register your models here.
admin.site.register(EmailOTP)

admin.site.register(Profile)