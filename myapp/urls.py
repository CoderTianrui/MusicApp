from django.urls import path
from .views import login_view, logout_view, session_view, get_csrf_token

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('session/', session_view, name='session'),
    path('get_csrf_token/', get_csrf_token, name='csrf'),
]
