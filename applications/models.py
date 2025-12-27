from django.db import models
from django.conf import settings

class Application(models.Model):
    """Membership application from prospective members"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Account info
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text="Requested username"
    )
    password = models.CharField(
        max_length=128,
        help_text="Password (will be hashed when account is created)"
    )
    email = models.EmailField(
        unique=True,
        help_text="Email address"
    )
    
    # Personal info
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    age = models.PositiveIntegerField()
    school = models.CharField(max_length=200)
    programming_experience = models.TextField(
        help_text="Describe your programming background"
    )
    why_join = models.TextField(
        help_text="Why do you want to join the club?"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection (if applicable)"
    )
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_applications'
    )
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
    
    def __str__(self):
        return f"{self.username} - {self.get_status_display()}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"