from django.urls import path
from . import views

app_name = 'moderation'

urlpatterns = [
    path('report/<int:user_id>/', views.report_user, name='report_user'),
    path('block/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('blocked/', views.blocked_users_list, name='blocked_users'),
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/<int:pk>/reviewed/', views.mark_report_reviewed, name='mark_reviewed'),
]