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

from django.contrib.sessions.models import Session

@csrf_exempt
def add_track_to_playlist(request):
    if request.method == "POST":
        try:
            # Get the JSON data from the request body
            data = json.loads(request.body)

            # Extract necessary fields from the request data
            playlist_id = data.get('playlist_id')
            track_id = data.get('track_id')

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

            if check_playlist_track_link_exists(playlist_id, track_id):
                return JsonResponse({"error": "Playlist-Track link already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            playlistTrack = add_track_to_playlist(playlist_id, track_id)

            # Return a success response
            return JsonResponse({
                "message": "Playlist created successfully",
                "track id": playlistTrack.track_id,
                "playlist_id": playlistTrack.playlist_id,
            }, status=201)

        except (UserData.DoesNotExist, Session.DoesNotExist):
            return JsonResponse({"error": "User or session not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_exempt
def share_playlist(request):
    if request.method == "POST":
        try:
            # Get the JSON data from the request body
            data = json.loads(request.body)

            # Extract necessary fields from the request data
            playlist_id = data.get('playlist_id')
            user_id = data.get('user_id')

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

            if check_shared_playlist_exists(playlist_id, user_id):
                return JsonResponse({"error": "Playlist-User link already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            sharedPlaylist = share_playlist_to_user(playlist_id, user_id)

            # Return a success response
            return JsonResponse({
                "message": "Playlist created successfully",
                "playlist_id": sharedPlaylist.playlist_id,
                "user_id": sharedPlaylist.user_id,
            }, status=201)

        except (UserData.DoesNotExist, Session.DoesNotExist):
            return JsonResponse({"error": "User or session not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_exempt
def link_track_to_artist(request):
    if request.method == "POST":
        try:
            # Get the JSON data from the request body
            data = json.loads(request.body)

            # Extract necessary fields from the request data
            artist_id = data.get('artist_id')
            track_id = data.get('track_id')

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

            if user.role != 0:
                return JsonResponse({"error": "User does not have permission."}, status=403)

            if check_track_artist_link_exists(artist_id, track_id):
                return JsonResponse({"error": "Artist-Track link already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            trackArtistJunction = create_track_artist_link(artist_id, track_id)

            # Return a success response
            return JsonResponse({
                "message": "Playlist created successfully",
                "artist_id": trackArtistJunction.artist_id,
                "track_id": trackArtistJunction.track_id,
            }, status=201)

        except (UserData.DoesNotExist, Session.DoesNotExist):
            return JsonResponse({"error": "User or session not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_exempt
def link_track_to_album(request):
    if request.method == "POST":
        try:
            # Get the JSON data from the request body
            data = json.loads(request.body)

            # Extract necessary fields from the request data
            album_id = data.get('album_id')
            track_id = data.get('track_id')

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

            if user.role != 0:
                return JsonResponse({"error": "User does not have permission."}, status=403)

            if check_track_album_link_exists(album_id, track_id):
                return JsonResponse({"error": "Album-Track link already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            trackAlbumJunction = create_track_album_link(album_id, track_id)

            # Return a success response
            return JsonResponse({
                "message": "Playlist created successfully",
                "album_id": trackAlbumJunction.album_id,
                "track_id": trackAlbumJunction.track_id,
            }, status=201)

        except (UserData.DoesNotExist, Session.DoesNotExist):
            return JsonResponse({"error": "User or session not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_exempt
def link_track_to_genre(request):
    if request.method == "POST":
        try:
            # Get the JSON data from the request body
            data = json.loads(request.body)

            # Extract necessary fields from the request data
            genre_id = data.get('genre_id')
            track_id = data.get('track_id')

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

            if user.role != 0:
                return JsonResponse({"error": "User does not have permission."}, status=403)

            if check_track_genre_exists(genre_id, track_id):
                return JsonResponse({"error": "Genre-Track link already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            trackGenreJunction = create_track_genre_link(genre_id, track_id)

            # Return a success response
            return JsonResponse({
                "message": "Playlist created successfully",
                "genre_id": trackGenreJunction.genre_id,
                "track_id": trackGenreJunction.track_id,
            }, status=201)

        except (UserData.DoesNotExist, Session.DoesNotExist):
            return JsonResponse({"error": "User or session not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_exempt
def link_album_to_artist(request):
    if request.method == "POST":
        try:
            # Get the JSON data from the request body
            data = json.loads(request.body)

            # Extract necessary fields from the request data
            album_id = data.get('album_id')
            artist_id = data.get('artist_id')

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

            if user.role != 0:
                return JsonResponse({"error": "User does not have permission."}, status=403)

            # Check if the album-artist link already exists
            if check_album_artist_link_exists(album_id, artist_id):
                return JsonResponse({"error": "Album-Artist link already exists"}, status=400)

            # Create a new album-artist link
            albumArtistJunction = create_album_artist_link(album_id, artist_id)

            # Return a success response
            return JsonResponse({
                "message": "Album-Artist link created successfully",
                "album_id": albumArtistJunction.album_id,
                "artist_id": albumArtistJunction.artist_id,
            }, status=201)

        except (UserData.DoesNotExist, Session.DoesNotExist):
            return JsonResponse({"error": "User or session not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_exempt
def remove_album_track_link(request):
    if request.method == "POST":
        try:
            # Get the JSON data from the request body
            data = json.loads(request.body)

            # Extract necessary fields from the request data
            album_id = data.get('album_id')
            artist_id = data.get('artist_id')

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

            if user.role != 0:
                return JsonResponse({"error": "User does not have permission."}, status=403)

            # Check if the album-artist link already exists
            if check_album_artist_link_exists(album_id, artist_id):
                return JsonResponse({"error": "Album-Artist link already exists"}, status=400)

            # Create a new album-artist link
            albumArtistJunction = create_album_artist_link(album_id, artist_id)

            # Return a success response
            return JsonResponse({
                "message": "Album-Artist link created successfully",
                "album_id": albumArtistJunction.album_id,
                "artist_id": albumArtistJunction.artist_id,
            }, status=201)

        except (UserData.DoesNotExist, Session.DoesNotExist):
            return JsonResponse({"error": "User or session not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)