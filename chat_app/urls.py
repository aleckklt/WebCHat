from django.urls import path
from . import views

app_name = 'chat_app'

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('<int:conversation_id>/', views.chat_room, name='chat_room'),
    path('create/', views.create_conversation, name='create_conversation'),
]