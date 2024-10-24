from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import login
from django.http import JsonResponse
from django.middleware.csrf import get_token
from .models import UserData
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
    create_track,
    add_track_to_playlist,
    share_playlist_to_user,
    create_album,
    create_genre,
    create_artist,
    create_track_artist_link,
    create_track_album_link,
    create_track_genre_link,
    create_album_artist_link,
    get_album
    )
import json
import re

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

@csrf_protect
def login_view(request):
    if request.method == "POST":
        body = json.loads(request.body)
        username = body.get('username')
        password = body.get('password')
        mfa_code = body.get('mfa_code')
        ip_address = request.META.get('REMOTE_ADDR')  # Get the user's IP address

        # Rate limit key (based on IP address and username)
        rate_limit_key = f"login_attempts_{username}_{ip_address}"

        # Check if the user has exceeded the allowed attempts
        attempts = cache.get(rate_limit_key, 0)
        if attempts >= 5:
            return JsonResponse({"error": "Too many failed login attempts. Please try again in 10 minutes."}, status=429)

        # Check if the username and password are provided
        if not username or not password:
            return JsonResponse({"error": "Username and password required"}, status=400)

        try:
            # Query the UserData table in AWS RDS (adjust the model name as needed)
            user = UserData.objects.get(email=username)

            # Check if the password matches using Django's password hashing system
            if check_password(password, user.password):

                totp = pyotp.TOTP(user.mfa_secret)
                if not totp.verify(mfa_code):
                    return JsonResponse({"error": "Invalid MFA code"}, status=400)
                # Use Django's login function to log in the user
                login(request, user)

                # Reset the failed attempts after a successful login
                cache.delete(rate_limit_key)

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
                # Increment failed login attempts
                attempts += 1
                cache.set(rate_limit_key, attempts, timeout=600)  # Set a 10-minute lockout after 5 failed attempts
                return JsonResponse({"error": "Invalid credentials"}, status=400)

        except UserData.DoesNotExist:
            # Increment failed login attempts
            attempts += 1
            cache.set(rate_limit_key, attempts, timeout=600)  # Set a 10-minute lockout after 5 failed attempts
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

        # Other registration checks...
        if UserData.objects.filter(email=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)

        # Hash the password

        password_regex = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{10,}$'
        if not re.match(password_regex, password):
            return JsonResponse({"error": "invalidPassword"}, status=400)
        
        hashed_password = make_password(password)

        # Generate a new MFA secret for the user
        mfa_secret = pyotp.random_base32()

        # If displayname is not provided, use name as displayname
        if not display_name:
            display_name = name

        # Save username (email), name, displayname, and MFA secret to the UserData model
        new_user = UserData.objects.create(
            email=username,
            password=hashed_password,
            name=name,
            display_name=display_name,
            role=1,
            mfa_secret=mfa_secret  # Save the MFA secret
        )

        # Generate a QR code for the user to scan in the authenticator app
        totp_uri = pyotp.totp.TOTP(mfa_secret).provisioning_uri(username, issuer_name="MusicFlow")
        img = qrcode.make(totp_uri)

        # Convert the QR code image to a base64 string to include in the response
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Return the QR code as a base64 string along with the success message
        return JsonResponse({
            "message": "User registered successfully",
            "qr_code": f"data:image/png;base64,{qr_code_base64}"
        }, status=201)

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

            if user.role != 0:
                return JsonResponse({"error": "User does not have permission."}, status=403)

            if check_track_exists(title):
                return JsonResponse({"error": "Track already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            track = create_track(title, duration, resource_link, release_date, lyrics, user)

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

            if user.role != 0:
                return JsonResponse({"error": "User does not have permission."}, status=403)

            if check_album_exists(title):
                return JsonResponse({"error": "Album already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            album = create_album(artist_id, title, release_date, cover_img_url, label, total_tracks, description, album_type)

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

            if user.role != 0:
                return JsonResponse({"error": "User does not have permission."}, status=403)

            if check_genre_exists(name):
                return JsonResponse({"error": "Genre already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            genre = create_genre(name, description, album_type)

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

            if user.role != 0:
                return JsonResponse({"error": "User does not have permission."}, status=403)

            if check_artist_exists(name):
                return JsonResponse({"error": "Artist already exists"}, status=400)

            # Create a new playlist and set the owner as the current user
            genre = create_artist(name, bio, profile_img_link, debut_date)

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
            data = json.loads(request.body)
            print(f"Full request body: {data}")
            music_name = data.get('music_name')
            print(f"Received music name: {music_name}")

            if not music_name:
                return JsonResponse({"error": "No music name provided"}, status=400)

            # Build the path to the music file
            music_file_path = os.path.join(SONGS_DIR, music_name)
            print(music_file_path)

            # Check if the file exists
            if not os.path.exists(music_file_path):
                return JsonResponse({"error": "Music file not found"}, status=404)

            return FileResponse(open(music_file_path, 'rb'), content_type='audio/flac')

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)



from django.http import JsonResponse
from .models import Track

def search_songs(request):
    query = request.GET.get('query', '')
    if query:
        songs = Track.objects.filter(title__icontains=query)  # 进行不区分大小写的模糊匹配
        song_list = [
            {
                'trackNumber': index + 1,
                'title': song.title,
                'duration': song.duration
            }
            for index, song in enumerate(songs)
        ]
        return JsonResponse(song_list, safe=False)
    return JsonResponse([], safe=False)



