from django.contrib import admin
from .models import Complaint,Comment
# Register your models here.
admin.site.register(Complaint)
admin.site.register(Comment)