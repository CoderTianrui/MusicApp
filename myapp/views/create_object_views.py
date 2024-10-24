from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import login
from django.http import JsonResponse
from django.middleware.csrf import get_token
from myapp.models import UserData
from myapp.database import (
    check_playlist_exists,
    check_track_exists,
    check_playlist_track_link_exists,
    check_shared_playlist_exists,
    check_album_exists,
    check_album_exists_by_cover_img_url,
    check_genre_exists,
    check_artist_exists,
    check_track_artist_link_exists,
    check_track_album_link_exists,
    check_track_genre_exists,
    check_album_artist_link_exists,
    create_playlist,
    create_track_database,
    add_track_to_playlist,
    share_playlist_to_user,
    create_album,
    create_genre,
    create_artist,
    create_track_artist_link,
    create_track_album_link,
    create_track_genre_link,
    create_album_artist_link,
    get_album,
    check_track_exists_by_resource_id
    )
import json
import re
import os
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from datetime import timedelta
import pyotp
import base64
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile


@csrf_exempt
def create_playlist(request):
    if request.method == "POST":
        try:
            # Get the JSON data from the request body
            data = json.loads(request.body)

            # Extract necessary fields from the request data
            title = data.get('title')

            # Get the session ID from cookies to identify the user
            session_key = request.COOKIES.get('sessionid')

            if not session_key:
                return JsonResponse({"error": "No session ID found in cookies"}, status=401)

            # Get the session data to retrieve the user ID
            session = Session.objects.get(session_key=session_key)
            session_data = session.get_decoded()
            user_id = session_data.get('_auth_user_id')

            if not user_id:
                return JsonResponse({"error": "User not authenticated"}, status=401)

            # Retrieve the user from the UserData model
            user = UserData.objects.get(pk=user_id)

            if check_playlist_exists(title):
                return JsonResponse({"error": "Playlist already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            playlist = create_playlist(title, user)

            # Return a success response
            return JsonResponse({
                "message": "Playlist created successfully",
                "playlist_id": playlist.playlist_id,
                "title": playlist.name,
                "owner": playlist.owner.email
            }, status=201)

        except (UserData.DoesNotExist, Session.DoesNotExist):
            return JsonResponse({"error": "User or session not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_protect
def add_track(request):
    if request.method == "POST":
        try:
            # Ensure that we are handling a multipart form submission
            if not request.FILES or not request.POST:
                return JsonResponse({"error": "Invalid multipart form data"}, status=400)
            
            session_key = request.COOKIES.get('authSessionid')

            if not session_key:
                return JsonResponse({"error": "No session ID found in cookies"}, status=401)

            # Get the session data to retrieve the user ID
            session = Session.objects.get(session_key=session_key)
            session_data = session.get_decoded()
            print(session_data)
            user_id = session_data.get('_auth_user_id')

            if not user_id:
                return JsonResponse({"error": "User not authenticated"}, status=401)

            # Retrieve the user from the UserData model
            user = UserData.objects.get(pk=user_id)

            if user.role != 0:
                return JsonResponse({"error": "User does not have permission."}, status=403)

            # Get form fields from the request
            title = request.POST.get('title')
            duration = request.POST.get('duration')
            release_date = request.POST.get('releaseDate')
            lyrics = request.POST.get('lyrics')

            # Get the uploaded music file from the request
            uploaded_file = request.FILES.get('file')

            # Check if all required fields are present
            if not all([title, duration, release_date, uploaded_file]):
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Check for duplicate title or resource_link (file name)
            if check_track_exists(title):
                return JsonResponse({"error": "A track with this title already exists."}, status=400)
            
            if check_track_exists_by_resource_id(uploaded_file.name):
                return JsonResponse({"error": "A track with this file name already exists."}, status=400)

            # Define the directory to store the music files
            music_directory = os.path.join(r'D:\projects\musicflow3\backend\database_storage\songs')
            if not os.path.exists(music_directory):
                os.makedirs(music_directory)

            # Save the music file to the tracks directory
            file_path = os.path.join(music_directory, uploaded_file.name)

            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Save the file name in the resource_link
            resource_link = uploaded_file.name  # For example, "still_here.flac"

            # Save the track data to the database (replace this with your actual DB logic)
            track = create_track_database(title, duration, resource_link, release_date, lyrics)

            # Return success response
            return JsonResponse({"message": "Track added successfully", "track_id": track.track_id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_protect
def add_album(request):
    if request.method == "POST":
        try:
            # Ensure that we are handling a multipart form submission
            if not request.FILES or not request.POST:
                return JsonResponse({"error": "Invalid multipart form data"}, status=400)
            
            session_key = request.COOKIES.get('authSessionid')

            if not session_key:
                return JsonResponse({"error": "No session ID found in cookies"}, status=401)

            # Get the session data to retrieve the user ID
            session = Session.objects.get(session_key=session_key)
            session_data = session.get_decoded()
            print(session_data)
            user_id = session_data.get('_auth_user_id')

            if not user_id:
                return JsonResponse({"error": "User not authenticated"}, status=401)

            # Retrieve the user from the UserData model
            user = UserData.objects.get(pk=user_id)

            if user.role != 0:
                return JsonResponse({"error": "User does not have permission."}, status=403)

            # Get form fields from the request
            title = request.POST.get('title')
            total_tracks = request.POST.get('totalTracks')
            label = request.POST.get('label')
            release_date = request.POST.get('releaseDate')
            description = request.POST.get('description')

            # Get the uploaded music file from the request
            uploaded_file = request.FILES.get('file')

            # Check if all required fields are present
            if not all([title, total_tracks, label, description, release_date, uploaded_file]):
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Check for duplicate title or resource_link (file name)
            if check_album_exists(title):
                return JsonResponse({"error": "An album with this title already exists."}, status=400)
            
            if check_album_exists_by_cover_img_url(uploaded_file.name):
                return JsonResponse({"error": "An album with this file name already exists."}, status=400)

            # Define the directory to store the music files
            music_directory = os.path.join(r'D:\projects\musicflow3\backend\database_storage\cover_imgs')
            if not os.path.exists(music_directory):
                os.makedirs(music_directory)

            # Save the file name in the resource_link
            resource_link = uploaded_file.name  # For example, "still_here.flac"

            # Save the track data to the database (replace this with your actual DB logic)
            album = create_album(title, release_date, resource_link, label, total_tracks, description)
            
            # Save the music file to the tracks directory
            file_path = os.path.join(music_directory, uploaded_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Return success response
            return JsonResponse({"message": "Album added successfully", "album_id": album.album_id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_protect
def add_artist(request):
    if request.method == "POST":
        try:
            # Ensure that we are handling a JSON submission
            if not request.body:
                return JsonResponse({"error": "Invalid JSON data"}, status=400)

            # Parse the JSON body of the request
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON format"}, status=400)

            session_key = request.COOKIES.get('authSessionid')

            if not session_key:
                return JsonResponse({"error": "No session ID found in cookies"}, status=401)

            # Get the session data to retrieve the user ID
            session = Session.objects.get(session_key=session_key)
            session_data = session.get_decoded()
            print(session_data)
            user_id = session_data.get('_auth_user_id')

            if not user_id:
                return JsonResponse({"error": "User not authenticated"}, status=401)

            # Retrieve the user from the UserData model
            user = UserData.objects.get(pk=user_id)

            if user.role != 0:
                return JsonResponse({"error": "User does not have permission."}, status=403)


            # Get form fields from the JSON data
            name = data.get('name')
            debut_date = data.get('debutDate')
            bio = data.get('bio')

            # Validate required fields
            if not all([name, debut_date]):
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Check for duplicate artist name
            if check_artist_exists(name):
                return JsonResponse({"error": "An artist with this name already exists."}, status=400)

            # Save the artist data to the database (replace this with your actual DB logic)
            artist = create_artist(name, bio, "example.com/name", debut_date)

            # Return success response
            return JsonResponse({"message": "Artist added successfully", "artist_id": artist.artist_id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_protect
def add_genre(request):
    if request.method == "POST":
        try:
            # Ensure that we are handling a JSON submission
            if not request.body:
                return JsonResponse({"error": "Invalid JSON data"}, status=400)

            # Parse the JSON body of the request
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON format"}, status=400)

            session_key = request.COOKIES.get('authSessionid')

            if not session_key:
                return JsonResponse({"error": "No session ID found in cookies"}, status=401)

            # Get the session data to retrieve the user ID
            session = Session.objects.get(session_key=session_key)
            session_data = session.get_decoded()
            user_id = session_data.get('_auth_user_id')

            if not user_id:
                return JsonResponse({"error": "User not authenticated"}, status=401)

            # Retrieve the user from the UserData model
            user = UserData.objects.get(pk=user_id)

            if user.role != 0:
                return JsonResponse({"error": "User does not have permission."}, status=403)


            # Get form fields from the JSON data
            name = data.get('name')
            description = data.get('description')

            # Validate required fields
            if not all([name, description]):
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Check for duplicate artist name
            if check_genre_exists(name):
                return JsonResponse({"error": "An artist with this name already exists."}, status=400)

            # Save the artist data to the database (replace this with your actual DB logic)
            genre = create_genre(name, description)

            # Return success response
            return JsonResponse({"message": "Genre added successfully", "genre_id": genre.genre_id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)