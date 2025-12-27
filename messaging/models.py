from django.db import models
from django.conf import settings

class Conversation(models.Model):
    """Private conversation between two users"""
    
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_as_user1'
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_as_user2'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user1', 'user2']
    
    def __str__(self):
        return f"{self.user1.username} ↔ {self.user2.username}"
    
    def get_other_user(self, current_user):
        """Get the other user in conversation"""
        return self.user2 if self.user1 == current_user else self.user1
    
    def unread_count(self, user):
        """Count unread messages for a user"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    """Private message"""
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        null=True,
        blank=True
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        null=True,
        blank=True
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Group message fields
    is_group_message = models.BooleanField(default=False)
    group_type = models.CharField(
        max_length=20,
        choices=[('all', 'All Members'), ('admin', 'Admins Only')],
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        if self.is_group_message:
            return f"{self.sender.username} → {self.group_type} group"
        return f"{self.sender.username} → {self.receiver.username}"


class FirstContactTracker(models.Model):
    """Track first contact message limits"""
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='first_contacts_sent'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='first_contacts_received'
    )
    message_count = models.PositiveIntegerField(default=0)
    receiver_replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['sender', 'receiver']
    
    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} ({self.message_count}/3)"
    
    @property
    def can_send_more(self):
        return self.receiver_replied or self.message_count < 3