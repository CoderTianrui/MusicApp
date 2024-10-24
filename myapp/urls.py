from django.urls import path
from .views import (login_view, logout_view, session_view, get_csrf_token, register_view, create_playlist, create_track, add_track_to_playlist,
                    share_playlist, make_album, make_genre, get_album_info, get_music, search_songs
                    )

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('session/', session_view, name='session'),
    path('get_csrf_token/', get_csrf_token, name='csrf'),
    path('register/', register_view, name='register'),
    path('create_playlist/', create_playlist, name='create_playlist'),
    path('create_track/', create_track, name='create_track'),
    path('add_track_to_playlist/', add_track_to_playlist, name='add_track_to_playlist'),
    path('share_playlist/', share_playlist, name='share_playlist'),
    path('make_album/', make_album, name='make_album'),
    path('make_genre/', make_genre, name='make_genre'),
    path('get_album/', get_album_info, name='get_album_info'),
    path('get_music/', get_music, name='get_music'),
    path('search_songs/', search_songs, name='search_songs')

]
