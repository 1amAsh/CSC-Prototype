from django.contrib import admin
from .models import Post, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('author', 'created_at')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'comment_count', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CommentInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'post__title', 'author__username')
    readonly_fields = ('created_at',)