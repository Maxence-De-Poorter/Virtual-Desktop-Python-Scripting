# agenda/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Event, Task

@login_required
def event_list(request):
    events = Event.objects.filter(user=request.user)
    return render(request, 'agenda/event_list.html', {'events': events})

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'agenda/task_list.html', {'tasks': tasks})

@login_required
def event_feed(request):
    events = Event.objects.filter(user=request.user)
    events_list = []
    for event in events:
        events_list.append({
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
        })
    return JsonResponse(events_list, safe=False)
