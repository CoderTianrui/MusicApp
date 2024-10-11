from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login
from django.http import JsonResponse
from django.middleware.csrf import get_token
from .models import UserData
import json

@csrf_protect 
def login_view(request):
    
    if request.method == "POST":
        body = json.loads(request.body)
        username = body.get('username')
        password = body.get('password')


        # Check if the username and password are provided
        if not username or not password:
            return JsonResponse(request, status=400)

        try:
            # Query the UserData table in AWS RDS
            user = UserData.objects.get(email=username)

            # Check if the password matches using Django's password hashing system
            if check_password(password, user.password):
                # Use Django's login function to log in the user
                login(request, user)
                return JsonResponse({"message": "Logged in successfully"}, status=200)
            else:
                return JsonResponse({"error": "Invalid credentials"}, status=400)
        
        except UserData.DoesNotExist:
            # Return error if the user does not exist
            return JsonResponse({"error": "Invalid credentials"}, status=400)
    
    return JsonResponse({"error": "Only POST method allowed"}, status=405)

def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logged out successfully"}, status=200)

def session_view(request):
    if request.user.is_authenticated:
        return JsonResponse({"user": request.user.username}, status=200)
    return JsonResponse({"error": "Not authenticated"}, status=401)

def get_csrf_token(request):
    csrf_token = get_token(request)
    print(csrf_token)
    return JsonResponse({"csrf_token": csrf_token})
