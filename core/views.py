from django.shortcuts import render

def home_view(request):
    """Role-based homepage - shows different content based on user role"""
    
    if not request.user.is_authenticated:
        # Guest homepage
        return render(request, 'core/home_guest.html')
    
    elif request.user.is_admin:
        # Admin dashboard
        context = {
            'total_members': request.user.__class__.objects.filter(role='member').count(),
            'total_admins': request.user.__class__.objects.filter(role='admin').count(),
        }
        return render(request, 'core/home_admin.html', context)
    
    else:
        # Member dashboard
        return render(request, 'core/home_member.html')

def about_view(request):
    """About the club page"""
    return render(request, 'core/about.html')