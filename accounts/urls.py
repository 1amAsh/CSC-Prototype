from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('members/', views.members_list_view, name='members'),
    path('members/<int:pk>/kick/', views.kick_member, name='kick_member'),
]