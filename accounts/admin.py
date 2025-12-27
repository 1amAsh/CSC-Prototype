from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile

class ProfileInline(admin.StackedInline):
    """Inline profile editing in user admin"""
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('age', 'school', 'programming_experience', 'bio')
    readonly_fields = []

class UserAdmin(BaseUserAdmin):
    """Custom User admin with role and profile"""
    
    inlines = (ProfileInline,)
    
    list_display = ('username', 'email', 'role', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Permissions', {'fields': ('role',)}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role & Permissions', {'fields': ('role', 'email')}),
    )

# Unregister the default User admin if it exists, then register our custom one
admin.site.unregister(User) if admin.site.is_registered(User) else None
admin.site.register(User, UserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Profile admin (can be accessed separately)"""
    list_display = ('user', 'get_full_name', 'school', 'age', 'is_complete', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'school')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_full_name(self, obj):
        return obj.full_name
    get_full_name.short_description = 'Full Name'
    
    def is_complete(self, obj):
        return obj.is_complete
    is_complete.boolean = True
    is_complete.short_description = 'Complete'