# agenda/views.py
from django.shortcuts import render, redirect
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

@login_required
def add_event(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        event = Event(title=title, description=description, start_time=start_time, end_time=end_time, user=request.user)
        event.save()
        return redirect('event_list')
    else:
        return render(request, 'agenda/add_event.html')

@login_required
def add_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        task = Task(title=title, description=description, due_date=due_date, user=request.user)
        task.save()
        return redirect('task_list')
    else:
        return render(request, 'agenda/add_task.html')

@login_required
def delete_event(request, event_id):
    event = Event.objects.get(id=event_id)
    event.delete()
    return redirect('event_list')

@login_required
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id)
    task.delete()
    return redirect('task_list')
