from django.urls import path
from . import views

app_name = 'chat_app'

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('create/', views.create_conversation, name='create_conversation'),
    path('create-group/', views.create_group_conversation, name='create_group'),
    path('group/<int:conversation_id>/manage/', views.manage_group, name='manage_group'),
    path('message/edit/', views.edit_message, name='edit_message'),
    path('message/delete/', views.delete_message, name='delete_message'),
    path('message/send/', views.send_message, name='send_message'),
]