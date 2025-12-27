from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.models import User
from .models import Application
from .forms import ApplicationForm

def apply_view(request):
    """Public application form for prospective members"""
    
    # Redirect if already logged in
    if request.user.is_authenticated:
        messages.info(request, "You're already a member!")
        return redirect('core:home')
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application submitted successfully! We will review it soon.')
            return redirect('core:home')
    else:
        form = ApplicationForm()
    
    return render(request, 'applications/apply.html', {'form': form})

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
def applications_dashboard(request):
    """Admin dashboard showing all applications"""
    
    pending = Application.objects.filter(status='pending')
    approved = Application.objects.filter(status='approved')
    rejected = Application.objects.filter(status='rejected')
    
    context = {
        'pending_applications': pending,
        'approved_count': approved.count(),
        'rejected_count': rejected.count(),
    }
    return render(request, 'applications/dashboard.html', context)

@admin_required
def application_detail(request, pk):
    """View single application detail"""
    application = get_object_or_404(Application, pk=pk)
    return render(request, 'applications/detail.html', {'application': application})

@admin_required
def approve_application(request, pk):
    """Approve application and create member account"""
    application = get_object_or_404(Application, pk=pk)
    
    if application.status != 'pending':
        messages.warning(request, 'This application has already been reviewed.')
        return redirect('applications:dashboard')
    
    # Store username before deleting application
    username = application.username
    
    # Create user account
    new_user = User.objects.create_user(
        username=application.username,
        email=application.email,
        password=application.password,
        first_name=application.first_name,
        last_name=application.last_name,
        role='member'
    )
    
    # Manually create profile with all required data
    from accounts.models import Profile
    Profile.objects.create(
        user=new_user,
        age=application.age,
        school=application.school,
        programming_experience=application.programming_experience
    )
    
    # Delete application (we created the account, no longer needed)
    application.delete()
    
    messages.success(request, f'Application approved! Account created for {username}.')
    return redirect('applications:dashboard')

@admin_required
def reject_application(request, pk):
    """Reject application with reason"""
    application = get_object_or_404(Application, pk=pk)
    
    if application.status != 'pending':
        messages.warning(request, 'This application has already been reviewed.')
        return redirect('applications:dashboard')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        application.status = 'rejected'
        application.rejection_reason = reason
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.save()
        
        messages.success(request, f'Application rejected.')
        return redirect('applications:dashboard')
    
    return render(request, 'applications/reject.html', {'application': application})