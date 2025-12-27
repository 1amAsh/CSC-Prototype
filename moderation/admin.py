from django.contrib import admin
from .models import Report, Block

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'reported_user', 'reason', 'reviewed', 'created_at')
    list_filter = ('reason', 'reviewed', 'created_at')
    search_fields = ('reporter__username', 'reported_user__username', 'description')

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('blocker', 'blocked', 'created_at')
    search_fields = ('blocker__username', 'blocked__username')