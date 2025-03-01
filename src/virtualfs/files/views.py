from django.http import JsonResponse
from .models import Video

def liste_videos(request):
    videos = Video.objects.values('title', 'file_path')
    return JsonResponse(list(videos), safe=False)
