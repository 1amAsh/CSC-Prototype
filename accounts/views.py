from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages

User = get_user_model()

def login_view(request):
    """Handle user login"""
    
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to appropriate page based on role
            next_url = request.GET.get('next', 'core:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('core:home')

@login_required
def profile_view(request):
    """View and edit user profile"""
    
    profile = request.user.profile
    
    if request.method == 'POST':
        # Update User model fields
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.save()
        
        # Update Profile fields
        profile.age = request.POST.get('age', None)
        profile.school = request.POST.get('school', '')
        profile.programming_experience = request.POST.get('programming_experience', '')
        profile.bio = request.POST.get('bio', '')
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    context = {
        'profile': profile,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def members_list_view(request):
    """View all club members and admins (visible to all logged-in users)"""
    from accounts.models import User
    
    admins = User.objects.filter(role='admin').select_related('profile').order_by('username')
    members = User.objects.filter(role='member').select_related('profile').order_by('username')
    
    context = {
        'admins': admins,
        'members': members,
        'total_admins': admins.count(),
        'total_members': members.count(),
        'total_participants': admins.count() + members.count(),
    }
    return render(request, 'accounts/members.html', context)

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

@admin_required
def kick_member(request, pk):
    """Kick a member (move to rejected applications and delete user)"""
    from accounts.models import User
    from applications.models import Application
    from django.utils import timezone
    
    member = get_object_or_404(User, pk=pk)
    
    # Cannot kick admins or yourself
    if member.is_admin:
        messages.error(request, 'Cannot kick an admin.')
        return redirect('accounts:members')
    
    if member == request.user:
        messages.error(request, 'Cannot kick yourself.')
        return redirect('accounts:members')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', 'Removed by admin')
        
        # Create rejected application from user data
        Application.objects.create(
            username=member.username,
            password='',  # Cannot retrieve hashed password
            email=member.email,
            first_name=member.first_name,
            last_name=member.last_name,
            age=member.profile.age,
            school=member.profile.school,
            programming_experience=member.profile.programming_experience,
            why_join='[User was removed from club]',
            status='rejected',
            rejection_reason=reason,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
            submitted_at=member.date_joined
        )
        
        # Store username before deleting
        username = member.username
        
        # Delete user (and profile via cascade)
        member.delete()
        
        messages.success(request, f'Member {username} has been removed from the club.')
        return redirect('accounts:members')
    
    return render(request, 'accounts/kick_member.html', {'member': member})