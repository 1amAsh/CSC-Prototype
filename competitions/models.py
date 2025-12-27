from django.db import models
from django.conf import settings

class Competition(models.Model):
    """Programming competition"""
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    max_score = models.PositiveIntegerField(default=100)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_competitions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    @property
    def total_participants(self):
        return self.submissions.values('user').distinct().count()
    
    @property
    def leaderboard(self):
        """Get sorted leaderboard"""
        submissions = self.submissions.select_related('user').order_by('-score', 'submitted_at')
        leaders = []
        seen_users = set()
        
        for submission in submissions:
            if submission.user_id not in seen_users:
                seen_users.add(submission.user_id)
                leaders.append(submission)
        
        return leaders


class Problem(models.Model):
    """Competition problem"""
    
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name='problems'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    points = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.competition.title} - {self.title}"


class Submission(models.Model):
    """User submission for a competition"""
    
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    solution = models.TextField(help_text="Code or text solution")
    score = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    scored_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scored_submissions'
    )
    scored_at = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-score', 'submitted_at']
        unique_together = ['competition', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.competition.title}"