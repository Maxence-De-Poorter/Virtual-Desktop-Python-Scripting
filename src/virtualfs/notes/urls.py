# notes/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('notes/', views.note_list, name='note_list'),
    path('notes/add/', views.add_note, name='add_note'),
    path('notes/delete/<int:note_id>/', views.delete_note, name='delete_note'),
]
