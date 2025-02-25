# views.py dans le dossier notes

from django.shortcuts import render, redirect
from .models import Note

def home(request):
    return render(request, 'home.html')

def note_list(request):
    notes = Note.objects.all()
    return render(request, 'note_list.html', {'notes': notes})

def add_note(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        note = Note(title=title, content=content)
        note.save()
        return redirect('note_list')
    else:
        return render(request, 'add_note.html')

def delete_note(request, note_id):
    note = Note.objects.get(id=note_id)
    note.delete()
    return redirect('note_list')
