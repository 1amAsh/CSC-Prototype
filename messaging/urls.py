from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('start/', views.start_conversation, name='start'),
    path('conversation/<int:user_id>/', views.conversation_view, name='conversation'),
    path('send/<int:user_id>/', views.send_message, name='send'),
    path('group/<str:group_type>/', views.group_chat, name='group_chat'),
    path('group/<str:group_type>/send/', views.send_group_message, name='send_group'),
    path('api/check-new/', views.check_new_messages, name='check_new'),
]