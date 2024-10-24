from django.urls import path

from myapp.views.auth_views import (
    login_view,
    register_view,
    logout_view,
    session_view,
    get_csrf_token
)

from myapp.views.create_object_views import (
    create_playlist,
    add_track,
    add_album,
    add_artist,
    add_genre
)

from myapp.views.data_request_views import (
    get_album_info,
    get_music
)

from myapp.views.linking_views import (
    add_track_to_playlist,
    share_playlist,
    link_track_to_artist,
    link_track_to_album,
    link_track_to_genre,
    link_album_to_artist,
    remove_album_track_link
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('session/', session_view, name='session'),
    path('get_csrf_token/', get_csrf_token, name='csrf'),
    path('register/', register_view, name='register'),
    path('create_playlist/', create_playlist, name='create_playlist'),
    path('add_track_to_playlist/', add_track_to_playlist, name='add_track_to_playlist'),
    path('share_playlist/', share_playlist, name='share_playlist'),
    path('get_album/', get_album_info, name='get_album_info'),
    path('get_music/', get_music, name='get_music'),
    path('add_track/', add_track, name='add_track'),
    path('add_album/', add_album, name='add_album'),
    path('add_artist/', add_artist, name='add_artist'),
    path('add_genre/', add_genre, name='add_genre'),
    path('link_track_to_album/', link_track_to_album, name='link_track_to_album'),
    path('link_album_to_artist/', link_album_to_artist, name='link_album_to_artist'),
    path('link_track_to_artist/', link_track_to_artist, name='link_track_to_artist'),
]
