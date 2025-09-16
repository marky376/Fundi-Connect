

from django.db import models

from django.contrib.auth.models import AbstractUser
from PIL import Image

class Notification(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email}: {self.message[:30]}"




from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image


class User(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('fundi', 'Fundi'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    onboarding_complete = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email


class FundiProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fundi_profile')
    skills = models.JSONField(default=list)  # Store skills as JSON array
    description = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    availability = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_jobs_completed = models.PositiveIntegerField(default=0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.email} - Fundi Profile"


class PortfolioImage(models.Model):
    fundi = models.ForeignKey(FundiProfile, on_delete=models.CASCADE, related_name='portfolio_images')
    image = models.ImageField(upload_to='portfolio/')
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.fundi.user.email} - Portfolio Image"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Resize image to optimize storage
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                img.save(self.image.path)
