from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    """Custom User model with role-based access"""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='member',
        help_text="User role: Admin (full access) or Member (limited access)"
    )
    
    email = models.EmailField(
        unique=True,
        help_text="Must be unique across all users"
    )
    
    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'admin'
    
    @property
    def is_club_member(self):
        """Check if user is a member"""
        return self.role == 'member'


class Profile(models.Model):
    """Extended profile information for users"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    age = models.PositiveIntegerField(
        help_text="User's age in years"
    )
    
    school = models.CharField(
        max_length=200,
        help_text="Current school/institution"
    )
    
    programming_experience = models.TextField(
        help_text="Description of programming background and experience"
    )
    
    bio = models.TextField(
        max_length=500,
        default="Hey! Just another fellow member in the club!",
        help_text="Short bio (max 500 characters)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
    
    def __str__(self):
        return f"Profile: {self.user.username}"
    
    @property
    def is_complete(self):
        """Auto-check if profile is complete (all required fields filled)"""
        return bool(
            self.user.first_name and 
            self.user.last_name and 
            self.age and 
            self.school and 
            self.programming_experience
        )
    
    @property
    def full_name(self):
        """Get full name from User model"""
        return f"{self.user.first_name} {self.user.last_name}".strip()


# Signal to auto-create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a profile when a new user is created"""
    if created:
        # Only create profile if it doesn't exist
        # Don't create with required fields - let the code handle it
        if not hasattr(instance, 'profile'):
            try:
                instance.profile
            except Profile.DoesNotExist:
                # Profile will be created manually by the view
                pass