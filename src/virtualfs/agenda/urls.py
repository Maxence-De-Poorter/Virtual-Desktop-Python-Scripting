# agenda/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('events/', views.event_feed, name='event_feed'),
    path('events/list/', views.event_list, name='event_list'),
    path('events/add/', views.add_event, name='add_event'),
    path('events/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('tasks/list/', views.task_list, name='task_list'),
    path('tasks/add/', views.add_task, name='add_task'),
    path('tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),
]
