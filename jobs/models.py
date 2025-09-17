from users.models import User
from django.db import models
class Message(models.Model):
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.email} to {self.recipient.email} for job {self.job.title}" 
from django.db import models
from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class Job(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    fundi = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_jobs')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='medium')
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5 stars
    customer_review_text = models.TextField(blank=True)  # Optional written review
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class JobImage(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='job_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.job.title}"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    fundi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    message = models.TextField()
    proposed_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['job', 'fundi']
    
    def __str__(self):
        return f"{self.fundi.email} applied for {self.job.title}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    fundi_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_made')
    fundi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_received', blank=True, null=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='payments', blank=True, null=True)

    def __str__(self):
        return f"Payment for {self.job.title} - {self.amount} ({self.status})"

class Review(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review for {self.job.title} - {self.rating} stars"
