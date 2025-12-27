from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('apply/', views.apply_view, name='apply'),
    path('dashboard/', views.applications_dashboard, name='dashboard'),
    path('<int:pk>/', views.application_detail, name='detail'),
    path('<int:pk>/approve/', views.approve_application, name='approve'),
    path('<int:pk>/reject/', views.reject_application, name='reject'),
]