from django.contrib import admin
from .models import Conversation, Message, FirstContactTracker

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'created_at', 'updated_at')
    search_fields = ('user1__username', 'user2__username')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'is_group_message', 'group_type', 'is_read', 'created_at')
    list_filter = ('is_group_message', 'is_read', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'content')

@admin.register(FirstContactTracker)
class FirstContactTrackerAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message_count', 'receiver_replied', 'created_at')
    list_filter = ('receiver_replied',)