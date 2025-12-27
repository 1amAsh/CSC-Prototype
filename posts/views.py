from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment
from .forms import PostForm, CommentForm

def admin_required(view_func):
    """Decorator to check if user is admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        if not request.user.is_admin:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
def posts_list(request):
    """View all posts (visible to all logged-in users)"""
    posts = Post.objects.all()
    context = {
        'posts': posts,
    }
    return render(request, 'posts/list.html', context)

@login_required
def post_detail(request, pk):
    """View single post with comments"""
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('posts:detail', pk=pk)
    else:
        form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/detail.html', context)

@admin_required
def post_create(request):
    """Create new post (admin only)"""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('posts:detail', pk=post.pk)
    else:
        form = PostForm()
    
    return render(request, 'posts/create.html', {'form': form})

@admin_required
def post_edit(request, pk):
    """Edit existing post (admin only)"""
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('posts:detail', pk=pk)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'posts/edit.html', {'form': form, 'post': post})

@admin_required
def post_delete(request, pk):
    """Delete post (admin only)"""
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('posts:list')
    
    return render(request, 'posts/delete.html', {'post': post})

@login_required
def comment_delete(request, pk):
    """Delete comment (author or admin only)"""
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    
    # Only author or admin can delete
    if request.user != comment.author and not request.user.is_admin:
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('posts:detail', pk=post_pk)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        return redirect('posts:detail', pk=post_pk)
    
    return render(request, 'posts/comment_delete.html', {'comment': comment})

@login_required
def comment_edit(request, pk):
    """Edit comment (author only)"""
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    
    # Only author can edit
    if request.user != comment.author:
        messages.error(request, 'You can only edit your own comments.')
        return redirect('posts:detail', pk=post_pk)
    
    if request.method == 'POST':
        new_content = request.POST.get('content', '')
        if new_content.strip():
            comment.content = new_content
            comment.save()
            messages.success(request, 'Comment updated successfully!')
            return redirect('posts:detail', pk=post_pk)
        else:
            messages.error(request, 'Comment cannot be empty.')
    
    return render(request, 'posts/comment_edit.html', {'comment': comment})