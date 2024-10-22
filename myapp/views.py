from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import login
from django.http import JsonResponse
from django.middleware.csrf import get_token
from .models import UserData, Playlist, Track, PlaylistTrack, SharedPlaylist, Album, Genre, Artist, TrackArtistJunction, TrackAlbumJunction, TrackGenreJunction, AlbumArtistJunction
import json
import re

from django.contrib.sessions.models import Session
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

@csrf_protect
def login_view(request):
    if request.method == "POST":
        body = json.loads(request.body)
        username = body.get('username')
        password = body.get('password')

        # Check if the username and password are provided
        if not username or not password:
            return JsonResponse({"error": "Username and password required"}, status=400)

        try:
            # Query the UserData table in AWS RDS (adjust the model name as needed)
            user = UserData.objects.get(email=username)

            # Check if the password matches using Django's password hashing system
            if check_password(password, user.password):
                # Use Django's login function to log in the user
                login(request, user)

                # Retrieve the session ID (session token)
                session_token = request.session.session_key

                if session_token is None:
                    # Ensure the session is created if it hasn't been yet
                    request.session.create()
                    session_token = request.session.session_key

                # Get the CSRF token
                csrf_token = get_token(request)

                # Create a response object
                response = JsonResponse({"message": "Logged in successfully", "session_token": session_token})

                # Set the sessionid cookie in the response
                response.set_cookie(
                    key='sessionid', 
                    value=session_token, 
                    httponly=True,  # Ensure that the session cookie is HTTP only
                    secure=False,  # Change to True if you're using HTTPS
                    samesite='Lax'  # Adjust the SameSite attribute as needed
                )

                # Set the csrftoken cookie in the response
                response.set_cookie(
                    key='csrftoken', 
                    value=csrf_token, 
                    httponly=False,  # Allow JavaScript access if needed
                    secure=False,  # Change to True if you're using HTTPS
                    samesite='Lax'  # Adjust the SameSite attribute as needed
                )

                return response
            else:
                return JsonResponse({"error": "Invalid credentials"}, status=400)
        
        except UserData.DoesNotExist:
            return JsonResponse({"error": "Invalid credentials"}, status=400)
    
    return JsonResponse({"error": "Only POST method allowed"}, status=405)

@csrf_protect 
def register_view(request):
    
    if request.method == "POST":
        body = json.loads(request.body)
        username = body.get('username')
        password = body.get('password')
        name = body.get('name')
        display_name = body.get('displayname')

        # 1. Check if username is in email format
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, username):
            return JsonResponse({"error": "usernameNotEmail"}, status=400)

        # 3. Check if name is provided
        if not name:
            return JsonResponse({"error": "nameNotGiven"}, status=400)

        # 2. Check if username (email) already exists in the UserData model
        if UserData.objects.filter(email=username).exists():
            return JsonResponse({"error": "existingUsername"}, status=400)

        # 4. Hash the password
        hashed_password = make_password(password)

        # 5. If displayname is not provided, use name as displayname
        if not display_name:
            display_name = name

        # 6. Save username (email), name, and displayname to the UserData model
        new_user = UserData.objects.create(
            email=username,        # 6. Save username to email
            password=hashed_password,  # 4. Save the hashed password
            name=name,             # 7. Save name to name
            display_name=display_name, # Save displayname (name if displayname not provided)
            role=1                 # 8. Set role to 1
        )

        return JsonResponse({"message": "User registered successfully"}, status=201)

    return JsonResponse({"error": "Only POST method allowed"}, status=405)

def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logged out successfully"}, status=200)

@csrf_exempt
def session_view(request):
    # Debugging: Print session info
    print(f"Session ID (from request.session): {request.session.session_key}")
    print(f"Session data: {request.session.get('_auth_user_id')}")
    print(f"Cookies: {request.COOKIES}")

    # Try to get session ID from cookies
    session_key = request.COOKIES.get('sessionid')
    if session_key:
        try:
            # Try to get the session from the Session table
            session = Session.objects.get(session_key=session_key)
            session_data = session.get_decoded()
            print(f"Session data: {session_data}")

            # Manually retrieve user ID from session data
            user_id = session_data.get('_auth_user_id')
            if user_id:
                try:
                    # Retrieve the user from the UserData model using the user_id
                    user = UserData.objects.get(pk=user_id)
                    return JsonResponse({"user": user.email}, status=200)
                except UserData.DoesNotExist:
                    return JsonResponse({"error": "User not found"}, status=404)

            else:
                return JsonResponse({"error": "No user ID in session data"}, status=401)

        except Session.DoesNotExist:
            return JsonResponse({"error": "Session does not exist"}, status=401)

    # If no session ID found in cookies
    return JsonResponse({"error": "No session ID found in cookies"}, status=401)

def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({"csrf_token": csrf_token})

@csrf_exempt
def create_playlist(request):
    if request.method == "POST":
        try:
            # Get the JSON data from the request body
            data = json.loads(request.body)

            # Extract necessary fields from the request data
            title = data.get('title')
            description = data.get('description', '')

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

            if Playlist.objects.filter(name=title).exists():
                return JsonResponse({"error": "Playlist already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            playlist = Playlist.objects.create(
                name=title,
                owner=user
            )

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

@csrf_exempt
def create_track(request):
    if request.method == "POST":
        try:
            # Get the JSON data from the request body
            data = json.loads(request.body)

            # Extract necessary fields from the request data
            title = data.get('title')
            duration = data.get('duration')
            resource_link = data.get('resource_link')
            release_date = data.get('release_date')
            lyrics = data.get('lyrics')

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

            if Track.objects.filter(title=title).exists():
                return JsonResponse({"error": "Track already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            track = Track.objects.create(
                title=title,
                duration=duration,
                resource_link=resource_link,
                release_date=release_date,
                lyrics=lyrics,
                owner=user
            )

            # Return a success response
            return JsonResponse({
                "message": "Playlist created successfully",
                "track id": track.track_id,
                "title": track.title,
                "resource_link": track.resource_link,
                "release_date": track.release_date,
                "lyrics": track.lyrics,
            }, status=201)

        except (UserData.DoesNotExist, Session.DoesNotExist):
            return JsonResponse({"error": "User or session not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

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

            if PlaylistTrack.objects.filter(playlist_id=playlist_id, track_id=track_id).exists():
                return JsonResponse({"error": "Playlist-Track link already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            playlistTrack = PlaylistTrack.objects.create(
                playlist_id=playlist_id,
                track_id=track_id,
            )

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

            if SharedPlaylist.objects.filter(playlist_id=playlist_id, user_id=user_id).exists():
                return JsonResponse({"error": "Playlist-User link already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            sharedPlaylist = SharedPlaylist.objects.create(
                playlist_id=playlist_id,
                user_id=user_id,
            )

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
def make_album(request):
    if request.method == "POST":
        try:
            # Get the JSON data from the request body
            data = json.loads(request.body)

            # Extract necessary fields from the request data
            artist_id = data.get('artist_id')
            title = data.get('title')
            release_date = data.get('release_date')
            cover_img_url = data.get('cover_img_url')
            label = data.get('label')
            total_tracks = data.get('total_tracks')
            description = data.get('description')
            album_type = data.get('album_type')

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

            if Album.objects.filter(title=title).exists():
                return JsonResponse({"error": "Album already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            album = Album.objects.create(
                artist_id=artist_id,
                title=title,
                release_date=release_date,
                cover_img_url=cover_img_url,
                label=label,
                total_tracks=total_tracks,
                description=description,
                album_type=album_type
            )

            # Return a success response
            return JsonResponse({
                "message": "Playlist created successfully",
                "artist_id": album.artist_id,
                "title": album.title,
            }, status=201)

        except (UserData.DoesNotExist, Session.DoesNotExist):
            return JsonResponse({"error": "User or session not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_exempt
def make_genre(request):
    if request.method == "POST":
        try:
            # Get the JSON data from the request body
            data = json.loads(request.body)

            # Extract necessary fields from the request data
            name = data.get('name')
            description = data.get('description')
            album_type = data.get('album_type')

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

            if Genre.objects.filter(name=name).exists():
                return JsonResponse({"error": "Genre already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            genre = Genre.objects.create(
                name=name,
                description=description,
                album_type=album_type
            )

            # Return a success response
            return JsonResponse({
                "message": "Playlist created successfully",
                "name": genre.name,
                "description": genre.description,
            }, status=201)

        except (UserData.DoesNotExist, Session.DoesNotExist):
            return JsonResponse({"error": "User or session not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_exempt
def make_artist(request):
    if request.method == "POST":
        try:
            # Get the JSON data from the request body
            data = json.loads(request.body)

            # Extract necessary fields from the request data
            name = data.get('name')
            bio = data.get('bio')
            profile_img_link = data.get('profile_img_link')
            debut_date = data.get('debut_date')

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

            if Artist.objects.filter(name=name).exists():
                return JsonResponse({"error": "Artist already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            genre = Artist.objects.create(
                name=name,
                bio=bio,
                profile_img_link=profile_img_link,
                debut_date=debut_date
            )

            # Return a success response
            return JsonResponse({
                "message": "Playlist created successfully",
                "name": genre.name,
                "description": genre.description,
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

            if TrackArtistJunction.objects.filter(artist_id=artist_id, track_id=track_id).exists():
                return JsonResponse({"error": "Artist-Track link already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            trackArtistJunction = TrackArtistJunction.objects.create(
                artist_id=artist_id,
                track_id=track_id,
            )

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

            if TrackAlbumJunction.objects.filter(album_id=album_id, track_id=track_id).exists():
                return JsonResponse({"error": "Album-Track link already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            trackAlbumJunction = TrackAlbumJunction.objects.create(
                album_id=album_id,
                track_id=track_id,
            )

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

            if TrackGenreJunction.objects.filter(genre_id=genre_id, track_id=track_id).exists():
                return JsonResponse({"error": "Genre-Track link already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            trackGenreJunction = TrackGenreJunction.objects.create(
                genre_id=genre_id,
                track_id=track_id,
            )

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

            # Check if the album-artist link already exists
            if AlbumArtistJunction.objects.filter(album_id=album_id, artist_id=artist_id).exists():
                return JsonResponse({"error": "Album-Artist link already exists"}, status=400)

            # Create a new album-artist link
            albumArtistJunction = AlbumArtistJunction.objects.create(
                album_id=album_id,
                artist_id=artist_id,
            )

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