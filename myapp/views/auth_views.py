from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import login
from django.http import JsonResponse
from django.middleware.csrf import get_token
from myapp.models import UserData
import json
import re

from django.contrib.sessions.models import Session
from django.core.cache import cache
import pyotp
import base64
import qrcode
from io import BytesIO

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
                    secure=True,  # Change to True if you're using HTTPS
                    samesite='Lax'  # Adjust the SameSite attribute as needed
                )

                # Set the csrftoken cookie in the response
                response.set_cookie(
                    key='csrftoken', 
                    value=csrf_token, 
                    httponly=False,  # Allow JavaScript access if needed
                    secure=True,  # Change to True if you're using HTTPS
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
    session_key = request.COOKIES.get('authSessionid')
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
                    return JsonResponse({"user": user.email, "role": user.role}, status=200)
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
