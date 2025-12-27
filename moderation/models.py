from django.db import models
from django.conf import settings

class Report(models.Model):
    """Member report system"""
    
    REASON_CHOICES = [
        ('harassment', 'Harassment'),
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('cheating', 'Cheating in Competition'),
        ('other', 'Other'),
    ]
    
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_made'
    )
    reported_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_received'
    )
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.reporter.username} reported {self.reported_user.username}"


class Block(models.Model):
    """User blocking system"""
    
    blocker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocks_made'
    )
    blocked = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocks_received'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['blocker', 'blocked']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"