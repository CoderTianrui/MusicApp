from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import HttpResponseRedirect
from myapp.models import Track, Album
from myapp.database import (
    get_album
    )
import json


@csrf_exempt
def get_album_info(request):
    if request.method == "POST":
        try:
            # Get the JSON data from the request body
            data = json.loads(request.body)

            # Extract necessary fields from the request data
            album_name = data.get('album_name')

            # Check if the album-artist link already exists
            album_data = get_album(album_name)

            if album_data.get("error"):
                return JsonResponse({
                    "message": "Album was not found",
                }, status=201)

            return JsonResponse({
                "message": "Album was found successfully",
                "album_data": album_data
            }, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

# import os
# SONGS_DIR = os.path.join('../backend', 'database_storage', 'songs')
import os
from django.http import JsonResponse, FileResponse
import json
from django.views.decorators.csrf import csrf_exempt

# Get the absolute path to the directory containing views.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SONGS_DIR = os.path.join(BASE_DIR, 'database_storage', 'songs')

print("BASE_DIR:", BASE_DIR)
print("SONGS_DIR:", SONGS_DIR)
from django.http import HttpResponse, JsonResponse
@csrf_exempt
def get_music(request):
    if request.method == "POST":
        try:
            # Get the JSON data from the request body
            data = json.loads(request.body)

            # Extract necessary fields from the request data
            music_name = data.get('music_name')

            if not music_name:
                return JsonResponse({"error": "No music name provided"}, status=400)

            # Build the path to the music file
            music_file_path = os.path.join(SONGS_DIR, music_name)

            # Check if the file exists
            if not os.path.exists(music_file_path):
                return JsonResponse({"error": "Music file not found"}, status=404)

            # Use X-Accel-Redirect header to serve the file via Nginx
            response = HttpResponse()
            response['X-Accel-Redirect'] = f"/protected_songs/{music_name}"
            response['Content-Type'] = 'audio/flac'  # Adjust the content type as needed
            return response

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_exempt
def search_songs(request):
    query = request.GET.get('query', '')
    if query:
        songs = Track.objects.filter(title__icontains=query)
        song_list = [
            {
                'trackNumber': index + 1,
                'title': song.title,
                'duration': song.duration,
                'url': song.resource_link
            }
            for index, song in enumerate(songs)
        ]
        return JsonResponse(song_list, safe=False)
    return JsonResponse([], safe=False)

@csrf_exempt
def search_albums(request):
    query = request.GET.get('query', '')
    if query:
        albums = Album.objects.filter(title__icontains=query)
        album_list = [
            {
                'albumNumber': index + 1,
                'title': album.title,
                'release_date': album.release_date,
                'label': album.label,
                'description': album.description
            }
            for index, album in enumerate(albums)
        ]
        return JsonResponse(album_list, safe=False)
    return JsonResponse([], safe=False)