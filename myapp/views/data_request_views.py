from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt

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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the songs directory
SONGS_DIR = os.path.join(BASE_DIR, '..', 'database_storage', 'songs')
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

            print(music_file_path)

            # Check if the file exists
            if not os.path.exists(music_file_path):
                return JsonResponse({"error": "Music file not found"}, status=404)

            # Return the file as a response (FileResponse handles streaming large files)
            return FileResponse(open(music_file_path, 'rb'), content_type='audio/flac')

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)