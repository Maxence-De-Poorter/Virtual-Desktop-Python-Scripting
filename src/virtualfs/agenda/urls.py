# agenda/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('events/', views.event_feed, name='event_feed'),
    path('', views.event_list, name='event_list'),
    path('tasks/', views.task_list, name='task_list'),
]
