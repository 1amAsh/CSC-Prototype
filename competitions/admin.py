from django.contrib import admin
from .models import Competition, Problem, Submission

class ProblemInline(admin.TabularInline):
    model = Problem
    extra = 1

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_date', 'end_date', 'total_participants', 'created_by')
    list_filter = ('status', 'start_date')
    search_fields = ('title', 'description')
    inlines = [ProblemInline]

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'competition', 'points', 'order')
    list_filter = ('competition',)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'competition', 'score', 'rank', 'submitted_at')
    list_filter = ('competition', 'submitted_at')
    search_fields = ('user__username', 'competition__title')