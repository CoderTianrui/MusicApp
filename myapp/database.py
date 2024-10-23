from .models import UserData, Playlist, Track, PlaylistTrack, SharedPlaylist, Album, Genre, Artist, TrackArtistJunction, TrackAlbumJunction, TrackGenreJunction, AlbumArtistJunction

def check_playlist_exists(title):
    result = Playlist.objects.filter(name=title).exists()
    return result

def check_track_exists(title):
    result = Track.objects.filter(title=title).exists()
    return result
    
def check_playlist_track_link_exists(playlist_id, track_id):
    result = PlaylistTrack.objects.filter(playlist_id=playlist_id, track_id=track_id).exists()
    return result

def check_shared_playlist_exists(playlist_id, user_id):
    result = SharedPlaylist.objects.filter(playlist_id=playlist_id, user_id=user_id).exists()
    return result

def check_album_exists(title):
    result = Album.objects.filter(title=title).exists()
    return result

def check_genre_exists(name):
    result = Genre.objects.filter(name=name).exists()
    return result

def check_artist_exists(name):
    result = Artist.objects.filter(name=name).exists()
    return result

def check_track_artist_link_exists(artist_id, track_id):
    result = TrackArtistJunction.objects.filter(artist_id=artist_id, track_id=track_id).exists()
    return result

def check_track_album_link_exists(album_id, track_id):
    result = TrackAlbumJunction.objects.filter(album_id=album_id, track_id=track_id).exists()
    return result

def check_track_genre_exists(genre_id, track_id):
    result = TrackGenreJunction.objects.filter(genre_id=genre_id, track_id=track_id).exists()
    return result

def check_album_artist_link_exists(album_id, artist_id):
    result = AlbumArtistJunction.objects.filter(album_id=album_id, artist_id=artist_id).exists()
    return result


def create_playlist(title, user):
    playlist = Playlist.objects.create(
                name=title,
                owner=user
            )
    return playlist

def create_track(title, duration, resource_link, release_date, lyrics, user):
    track = Track.objects.create(
                    title=title,
                    duration=duration,
                    resource_link=resource_link,
                    release_date=release_date,
                    lyrics=lyrics,
                    owner=user
                )
    return track

def add_track_to_playlist(playlist_id, track_id):
    playlistTrack = PlaylistTrack.objects.create(
                    playlist_id=playlist_id,
                    track_id=track_id,
                )
    return playlistTrack
    
def share_playlist_to_user(playlist_id, user_id):
    sharedPlaylist = SharedPlaylist.objects.create(
                    playlist_id=playlist_id,
                    user_id=user_id,
                )
    return sharedPlaylist
    
def create_album(artist_id, title, release_date, cover_img_url, label, total_tracks, description, album_type):
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
    return album
    
def create_genre(name, description, album_type):
    genre = Genre.objects.create(
                    name=name,
                    description=description,
                    album_type=album_type
                )
    return genre
    
def create_artist(name, bio, profile_img_link, debut_date):
    artist = Artist.objects.create(
                    name=name,
                    bio=bio,
                    profile_img_link=profile_img_link,
                    debut_date=debut_date
                )
    return artist
    
def create_track_artist_link(artist_id, track_id):
    trackArtistJunction = TrackArtistJunction.objects.create(
                    artist_id=artist_id,
                    track_id=track_id,
                )
    return trackArtistJunction

def create_track_album_link(album_id, track_id):  
    trackAlbumJunction = TrackAlbumJunction.objects.create(
                    album_id=album_id,
                    track_id=track_id
                )
    return trackAlbumJunction
    
def create_track_genre_link(genre_id, track_id):
    trackGenreJunction = TrackGenreJunction.objects.create(
                    genre_id=genre_id,
                    track_id=track_id,
                )
    return trackGenreJunction
    
def create_album_artist_link(album_id, artist_id):
    albumArtistJunction = AlbumArtistJunction.objects.create(
                    album_id=album_id,
                    artist_id=artist_id,
                )
    return albumArtistJunction


def remove_artist_by_name(name):
    artist = Artist.objects.filter(name=name).first()
    
    if not artist:
        return {"message": f"No artist found with the name {name}"}

    artist_id = artist.id
    
    track_artist_deleted, _ = TrackArtistJunction.objects.filter(artist_id=artist_id).delete()
    
    album_artist_deleted, _ = AlbumArtistJunction.objects.filter(artist_id=artist_id).delete()
    
    artist_deleted, _ = Artist.objects.filter(name=name).delete()
    
    total_deleted = track_artist_deleted + album_artist_deleted + artist_deleted

    return {
        "message": f"Successfully removed artist {name}",
        "artist_deleted": artist_deleted,
        "track_artist_links_deleted": track_artist_deleted,
        "album_artist_links_deleted": album_artist_deleted,
        "total_deleted": total_deleted
    }

def remove_album_by_name(title):
    album = Album.objects.filter(title=title).first()
    
    if not album:
        return {"message": f"No album found with the name {album}"}

    album_id = album.id
    
    track_album_deleted, _ = TrackAlbumJunction.objects.filter(album_id=album_id).delete()
    
    album_artist_deleted, _ = AlbumArtistJunction.objects.filter(album_id=album_id).delete()
    
    album_deleted, _ = Album.objects.filter(title=title).delete()
    
    total_deleted = track_album_deleted + album_artist_deleted + album_deleted

    return {
        "message": f"Successfully removed album {title}",
        "album_deleted": album_deleted,
        "track_artist_links_deleted": track_album_deleted,
        "album_artist_links_deleted": album_artist_deleted,
        "total_deleted": total_deleted
    }

def remove_genre_by_name(name):
    genre = Genre.objects.filter(name=name).first()
    
    if not genre:
        return {"message": f"No genre found with the name {genre}"}

    genre_id = genre.id
    
    track_genre_deleted, _ = TrackGenreJunction.objects.filter(genre_id=genre_id).delete()
    
    genre_deleted, _ = Genre.objects.filter(name=name).delete()
    
    total_deleted = track_genre_deleted + genre_deleted

    return {
        "message": f"Successfully removed artist {name}",
        "genre_deleted": genre_deleted,
        "track_genre_links_deleted": track_genre_deleted,
        "total_deleted": total_deleted
    }

def remove_track_by_name(title):
    track = Track.objects.filter(title=title).first()
    
    if not track:
        return {"message": f"No track found with the name {track}"}

    track_id = track.id
    
    track_playlist_deleted, _ = PlaylistTrack.objects.filter(track_id=track_id).delete()
    track_artist_deleted, _ = TrackArtistJunction.objects.filter(track_id=track_id).delete()
    track_album_deleted, _ = TrackAlbumJunction.objects.filter(track_id=track_id).delete()
    track_genre_deleted, _ = TrackGenreJunction.objects.filter(track_id=track_id).delete()
    
    track_deleted, _ = Track.objects.filter(name=title).delete()
    
    total_deleted = track_playlist_deleted + track_artist_deleted + track_album_deleted + track_genre_deleted + track_deleted

    return {
        "message": f"Successfully removed track {title}",
        "track_deleted": track_deleted,
        "track_playlist_links_deleted": track_playlist_deleted,
        "track_artist_links_deleted": track_artist_deleted,
        "track_album_links_deleted": track_album_deleted,
        "track_genre_links_deleted": track_genre_deleted,
        "total_deleted": total_deleted
    }

def remove_playlist(name):
    playlist = Playlist.objects.filter(name=name).first()
    
    if not playlist:
        return {"message": f"No playlist found with the name {playlist}"}

    playlist_id = playlist.id
    
    shared_playlist_deleted, _ = SharedPlaylist.objects.filter(playlist_id=playlist_id).delete()
    track_playlist_deleted, _ = PlaylistTrack.objects.filter(playlist_id=playlist_id).delete()
    
    playlist_deleted, _ = Playlist.objects.filter(name=name).delete()
    
    total_deleted = track_playlist_deleted + shared_playlist_deleted + playlist_deleted

    return {
        "message": f"Successfully removed track {playlist_id}",
        "playlist_deleted": playlist_deleted,
        "shared_playlist_links_deleted": shared_playlist_deleted,
        "track_playlist_links_deleted": track_playlist_deleted,
        "total_deleted": total_deleted
    }

def remove_user(email):
    user = UserData.objects.filter(email=email).first()
    
    if not user:
        return {"message": f"No user found with the name {user}"}

    user_id = user.id
    
    playlist_deleted, _ = Playlist.objects.filter(owner=user_id).delete()
    shared_playlist_deleted, _ = SharedPlaylist.objects.filter(user_id=user_id).delete()
    
    user_deleted, _ = UserData.objects.filter(email=email).delete()
    
    total_deleted = playlist_deleted + shared_playlist_deleted + user_deleted

    return {
        "message": f"Successfully removed user {email}",
        "user_deleted": user_deleted,
        "playlist_deleted": playlist_deleted,
        "shared_playlist_deleted": shared_playlist_deleted,
        "total_deleted": total_deleted
    }

def remove_user_from_shared_playlist(email, playlist_id):
    user = UserData.objects.filter(email=email).first()
    
    if not user:
        return {"message": f"No user found with the name {user}"}

    user_id = user.id
    
    shared_playlist_deleted, _ = SharedPlaylist.objects.filter(user_id=user_id, playlist_id=playlist_id).delete()

    return {
        "message": f"Successfully removed user {email} from shared playlist {playlist_id}",
        "shared_playlist_deleted": shared_playlist_deleted
    }

def remove_track_from_playlist(track_id, playlist_id):
    track = Track.objects.filter(track_id=track_id).first()
    playlist = Playlist.objects.filter(playlist_id=playlist_id).first()
    
    if not track:
        return {"message": f"No track found with the name {track}"}
    
    if not playlist:
        return {"message": f"No playlist found with the name {playlist}"}

    track_playlist_deleted, _ = PlaylistTrack.objects.filter(track_id=track_id, playlist_id=playlist_id).delete()

    return {
        "message": f"Successfully removed track {track_id} from playlist {playlist_id}",
        "track_playlist_deleted": track_playlist_deleted
    }

def remove_track_from_genre(track_id, genre_id):
    track = Track.objects.filter(track_id=track_id).first()
    genre = Genre.objects.filter(genre_id=genre_id).first()
    
    if not track:
        return {"message": f"No track found with the name {track}"}
    
    if not genre:
        return {"message": f"No genre found with the name {genre}"}

    track_genre_deleted, _ = TrackGenreJunction.objects.filter(track_id=track_id, genre_id=genre_id).delete()

    return {
        "message": f"Successfully removed track {track_id} from genre {genre_id}",
        "track_genre_deleted": track_genre_deleted
    }

def remove_track_from_artist(track_id, artist_id):
    track = Track.objects.filter(track_id=track_id).first()
    artist = Artist.objects.filter(artist_id=artist_id).first()
    
    if not track:
        return {"message": f"No track found with the name {track}"}
    
    if not artist:
        return {"message": f"No artist found with the name {artist}"}

    track_artist_deleted, _ = TrackArtistJunction.objects.filter(track_id=track_id, artist_id=artist_id).delete()

    return {
        "message": f"Successfully removed track {track_id} from artist {artist_id}",
        "track_artist_deleted": track_artist_deleted
    }

def remove_track_from_album(track_id, album_id):
    track = Track.objects.filter(track_id=track_id).first()
    album = Album.objects.filter(album_id=album_id).first()
    
    if not track:
        return {"message": f"No track found with the name {track}"}
    
    if not album:
        return {"message": f"No album found with the name {album}"}

    track_album_deleted, _ = TrackAlbumJunction.objects.filter(track_id=track_id, album_id=album_id).delete()

    return {
        "message": f"Successfully removed track {track_id} from album {album_id}",
        "track_album_deleted": track_album_deleted
    }

def remove_artist_from_album(album_id, artist_id):
    album = Album.objects.filter(album_id=album_id).first()
    artist = Artist.objects.filter(artist_id=artist_id).first()
    
    if not artist:
        return {"message": f"No artist found with the name {artist}"}
    
    if not album:
        return {"message": f"No album found with the name {album}"}

    artist_album_deleted, _ = AlbumArtistJunction.objects.filter(album_id=album_id, artist_id=artist_id).delete()

    return {
        "message": f"Successfully removed artist {artist_id} from album {album_id}",
        "artist_album_deleted": artist_album_deleted
    }

def remove_album_from_genre(album_id, genre_id):
    album = Album.objects.filter(album_id=album_id).first()
    genre = Genre.objects.filter(genre_id=genre_id).first()
    
    if not genre:
        return {"message": f"No genre found with the name {genre}"}
    
    if not album:
        return {"message": f"No album found with the name {album}"}

    genre_album_deleted, _ = AlbumArtistJunction.objects.filter(album_id=album_id, genre_id=genre_id).delete()

    return {
        "message": f"Successfully removed album {album_id} from genre {genre_id}",
        "genre_album_deleted": genre_album_deleted
    }


def get_album(title):
    # Find the album by title
    album = Album.objects.filter(title=title).first()

    if not album:
        return {"error": f"No album found with the title {title}"}

    album_id = album.album_id
    
    # Find all tracks associated with the album by searching TrackAlbumJunction by album id
    track_junctions = TrackAlbumJunction.objects.filter(album_id=album_id)
    track_ids = [tj.track_id for tj in track_junctions]
    tracks = Track.objects.filter(track_id__in=track_ids)
    
    # Find the artist associated with the album in AlbumArtistJunction by album id
    album_artist_junction = AlbumArtistJunction.objects.filter(album_id=album_id).first()
    if album_artist_junction:
        artist = Artist.objects.filter(artist_id=album_artist_junction.artist_id).first()
    else:
        artist = None

    # Compile the album, track, and artist data into a dictionary
    album_data = {
        "title": album.title,
        "release_date": album.release_date,
        "cover_img_url": album.cover_image_url,
        "label": album.label,
        "total_tracks": album.total_tracks,
        "description": album.description,
        "tracks": [{"title": track.title, "duration": track.duration, "resource_link": track.resource_link, "release_date": track.release_date, "lyrics": track.lyrics} for track in tracks],
        "artist": {
            "name": artist.name,
            "bio": artist.bio,
            "profile_img_link": artist.profile_image_url,
            "debut_date": artist.debut_date
        } if artist else None
    }

    return album_data