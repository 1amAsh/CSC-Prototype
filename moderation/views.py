from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import User
from .models import Report, Block
from .forms import ReportForm

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
def report_user(request, user_id):
    """Report a user"""
    reported_user = get_object_or_404(User, pk=user_id)
    
    # Cannot report yourself or admins
    if reported_user == request.user:
        messages.error(request, 'You cannot report yourself.')
        return redirect('accounts:members')
    
    if reported_user.is_admin:
        messages.error(request, 'You cannot report admins.')
        return redirect('accounts:members')
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.reported_user = reported_user
            report.save()
            messages.success(request, 'Report submitted successfully. Admins will review it.')
            return redirect('accounts:members')
    else:
        form = ReportForm()
    
    return render(request, 'moderation/report.html', {
        'form': form,
        'reported_user': reported_user,
    })

@login_required
def block_user(request, user_id):
    """Block a user"""
    blocked_user = get_object_or_404(User, pk=user_id)
    
    # Cannot block yourself or admins
    if blocked_user == request.user:
        messages.error(request, 'You cannot block yourself.')
        return redirect('accounts:members')
    
    if blocked_user.is_admin:
        messages.error(request, 'You cannot block admins.')
        return redirect('accounts:members')
    
    # Check if already blocked
    if Block.objects.filter(blocker=request.user, blocked=blocked_user).exists():
        messages.info(request, 'User is already blocked.')
        return redirect('moderation:blocked_users')
    
    Block.objects.create(blocker=request.user, blocked=blocked_user)
    messages.success(request, f'You have blocked {blocked_user.username}.')
    return redirect('moderation:blocked_users')

@login_required
def unblock_user(request, user_id):
    """Unblock a user"""
    blocked_user = get_object_or_404(User, pk=user_id)
    
    block = Block.objects.filter(blocker=request.user, blocked=blocked_user).first()
    if block:
        block.delete()
        messages.success(request, f'You have unblocked {blocked_user.username}.')
    else:
        messages.error(request, 'User is not blocked.')
    
    return redirect('moderation:blocked_users')

@login_required
def blocked_users_list(request):
    """View list of blocked users"""
    blocked = Block.objects.filter(blocker=request.user).select_related('blocked')
    
    return render(request, 'moderation/blocked_list.html', {
        'blocked_users': blocked,
    })

@admin_required
def reports_dashboard(request):
    """Admin dashboard for viewing reports"""
    unreviewed = Report.objects.filter(reviewed=False).select_related('reporter', 'reported_user')
    reviewed = Report.objects.filter(reviewed=True).select_related('reporter', 'reported_user')[:20]
    
    return render(request, 'moderation/reports_dashboard.html', {
        'unreviewed_reports': unreviewed,
        'reviewed_reports': reviewed,
    })

@admin_required
def mark_report_reviewed(request, pk):
    """Mark a report as reviewed"""
    report = get_object_or_404(Report, pk=pk)
    report.reviewed = True
    report.save()
    messages.success(request, 'Report marked as reviewed.')
    return redirect('moderation:reports_dashboard')