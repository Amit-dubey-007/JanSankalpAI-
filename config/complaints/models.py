from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
# Create your models here.

class Complaint(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="complaints")

    title = models.CharField(max_length=150)

    description = models.TextField(blank=True)

    # image = models.ImageField(upload_to='complaints_images/', blank=True, null=True)

    # voice = models.FileField(upload_to="complaints_voice/",blank=True,null=True)

    image = CloudinaryField(
        "image",
        folder="complaints/images",
        blank=True,
        null=True
    )

    voice = models.URLField(
        blank=True,
        null=True
    )

    voice_public_id = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )

    state = models.CharField(max_length=50)

    district = models.CharField(max_length=50)

    address = models.TextField(max_length=200)

    latitude= models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    longitude= models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True,db_index=True)

    updated_at = models.DateTimeField(auto_now=True)

    VISIBILITY_CHOICES = [
        # ("PUBLIC", "Public"),
        ("ANONYMOUS", "Anonymous"),
        ("GOVT ONLY", "Government Only"),
    ]

    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default="ANONYMOUS"
    )

    #private public post

    # ----------------- AI analysis fields ------------------

    is_valid = models.BooleanField(default=True,db_index=True)  # True if valid, False if invalid, None if not analyzed yet

    invalid_reason = models.TextField(blank=True)

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
        ("Rejected", "Rejected"),
    ] 

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending",db_index=True)

    analysis_status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Processing", "Processing"),
            ("Completed", "Completed"),
            ("Failed", "Failed"),
        ],
        default="Pending"
    )

    SEVERITY_CHOICES = [
        ("Low","Low"),
        ("Medium","Medium"),
        ("High","High"),
        ("Critical","Critical"),
    ]

    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, blank=True,db_index=True)

    severity_reason = models.TextField(blank=True)

    CATEGORY_CHOICES = [
        ("Road Infrastructure","Road Infrastructure"),
        ("Water","Water"),
        ("Electricity","Electricity"),
        ("Street Lighting","Street Lighting"),
        ("Healthcare","Healthcare"),
        ("Education","Education"),
        ("Sanitation & Garbage","Sanitation & Garbage"),
        ("Environment","Environment"),
        ("Public Transport","Public Transport"),
        ("Public Safety","Public Safety"),
        ("Government Services","Government Services"),
        ("Other","Other"),
    ]

    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, blank=True,db_index=True)

    priority_score = models.PositiveSmallIntegerField( blank=True,null=True) #range 1-100

    ai_confidence = models.FloatField(blank=True,null=True)

    ai_summary = models.TextField(blank=True)

    original_language = models.CharField(max_length=30,blank=True)

    english_translation = models.TextField(blank=True)

    voice_transcript = models.TextField(blank=True)

    suggested_actions = models.TextField(blank=True)

    keywords = models.JSONField(
        default=list,
        blank=True
    )

    department = models.CharField(max_length=100, blank=True,db_index=True)

    is_supported = models.BooleanField(default=False)

    is_followed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        if self.voice:
            self.voice.delete(save=False)
        super().delete(*args, **kwargs)

class ComplaintSupport(models.Model):
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name="supports",
        db_index=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["complaint", "user"],
                name="unique_support_per_user",
            )
        ]

class Comment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="comments",db_index=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="complaint_comments",db_index=True)

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    # updated_at = models.DateTimeField(auto_now=True)

    # is_edited = models.BooleanField(default=False)

    is_government = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.complaint.title}"
    
class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follows",db_index=True)
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="followers",db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "complaint"],
                name="unique_follow_per_user",
            )
        ]

class Notification(models.Model):

    TYPE_CHOICES = [
        ("Status", "Status"),
        ("Comment", "Comment"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    complaint = models.ForeignKey(
        "Complaint",
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=100)

    message = models.TextField(max_length=300)

    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title