from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path("chat-home/", views.chathome, name="chathome"),
    path('chat_initiate/', views.chat_intiate, name='chat'),
    path('chat/<slug:slug>/', views.chat_room, name='chat'),
    path('send_message/', views.send_message, name='send_message'),
    path('logout/', views.logout, name='logout'),
]
