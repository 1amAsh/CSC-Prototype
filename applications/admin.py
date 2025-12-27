from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'email', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('submitted_at', 'reviewed_at', 'reviewed_by')
    
    fieldsets = (
        ('Account Information', {
            'fields': ('username', 'email', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'age', 'school', 'programming_experience', 'why_join')
        }),
        ('Review Status', {
            'fields': ('status', 'rejection_reason', 'submitted_at', 'reviewed_at', 'reviewed_by')
        }),
    )