from django.urls import path
from . import views

app_name = 'competitions'

urlpatterns = [
    path('', views.competition_list, name='list'),
    path('create/', views.competition_create, name='create'),
    path('<int:pk>/', views.competition_detail, name='detail'),
    path('<int:pk>/edit/', views.competition_edit, name='edit'),
    path('<int:pk>/delete/', views.competition_delete, name='delete'),
    path('<int:pk>/leaderboard/', views.competition_leaderboard, name='leaderboard'),
    path('<int:pk>/submit/', views.submit_solution, name='submit'),
    path('<int:pk>/submissions/', views.submissions_list, name='submissions'),
    path('<int:competition_pk>/problem/add/', views.problem_add, name='problem_add'),
    path('submission/<int:pk>/score/', views.score_submission, name='score_submission'),
]