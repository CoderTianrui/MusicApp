from django.db import models

class UserData(models.Model):
    user_id = models.AutoField(primary_key=True)  # Primary key
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # Should be securely stored
    display_name = models.CharField(max_length=255)
    role = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)  # Creation time
    updated_at = models.DateTimeField(auto_now=True)      # Update time
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'UserData'  # Ensure it matches the database table name

class ActivityLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, null=True)  # Foreign key to UserData, nullable
    activity_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ActivityLog'

class Playlist(models.Model):
    playlist_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(UserData, on_delete=models.CASCADE, null=True)  # Foreign key to UserData, nullable
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'Playlist'

class SharedPlaylist(models.Model):
    share_id = models.AutoField(primary_key=True)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=True)  # Foreign key to Playlist, nullable
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, null=True)      # Foreign key to UserData, nullable
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'SharedPlaylist'

class PlaylistTrack(models.Model):
    playlist_track_id = models.AutoField(primary_key=True)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=True)  # Foreign key to Playlist, nullable
    track = models.ForeignKey('Track', on_delete=models.CASCADE, null=True)      # Foreign key to Track, nullable
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'PlaylistTrack'

class UserPlayHistory(models.Model):
    history_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, null=True)      # Foreign key to UserData, nullable
    track = models.ForeignKey('Track', on_delete=models.CASCADE, null=True)      # Foreign key to Track, nullable
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'UserPlayHistory'

class ManagementSetting(models.Model):
    manage_setting_id = models.AutoField(primary_key=True)
    setting_key = models.CharField(max_length=255)
    setting_value = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Added updated_at field

    class Meta:
        db_table = 'ManagementSetting'

class IpBanList(models.Model):
    ban_id = models.AutoField(primary_key=True)
    ip_address = models.CharField(max_length=255)
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, null=True)      # Foreign key to UserData, nullable
    reason = models.TextField()
    banned_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)

    class Meta:
        db_table = 'IpBanList'

class UserSetting(models.Model):
    setting_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, null=True)      # Foreign key to UserData, nullable
    audio_quality_setting = models.IntegerField()
    darkmode_setting = models.IntegerField()
    dynamic_color_setting = models.IntegerField()
    keyboard_shortcut = models.IntegerField()

    class Meta:
        db_table = 'UserSetting'

class KeyboardShortcut(models.Model):
    shortcut_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, null=True)      # Foreign key to UserData, nullable
    action = models.CharField(max_length=255)
    key_combination = models.CharField(max_length=50)  # According to your schema, length is 50
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'KeyboardShortcut'

class Track(models.Model):
    track_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    duration = models.IntegerField()  # In seconds
    resource_link = models.CharField(max_length=512)
    release_date = models.DateField()
    lyrics = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Track'

class TrackAlbumJunction(models.Model):
    junction_id = models.AutoField(primary_key=True)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, null=True)        # Foreign key to Track, nullable
    album = models.ForeignKey('Album', on_delete=models.CASCADE, null=True)      # Foreign key to Album, nullable
    track_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'TrackAlbumJunction'

class TrackGenreJunction(models.Model):
    junction_id = models.AutoField(primary_key=True)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, null=True)        # Foreign key to Track, nullable
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE, null=True)      # Foreign key to Genre, nullable
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'TrackGenreJunction'

class Genre(models.Model):
    genre_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Genre'

class Album(models.Model):
    album_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    cover_image_url = models.CharField(
        max_length=512,
        default="https://example.com/default_cover_image.jpg"
    )
    label = models.CharField(max_length=255)
    total_tracks = models.IntegerField(null=True, blank=True)  # Set total_tracks as nullable
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Album'

class TrackArtistJunction(models.Model):
    junction_id = models.AutoField(primary_key=True)
    artist = models.ForeignKey('Artist', on_delete=models.CASCADE, null=True)    # Foreign key to Artist, nullable
    track = models.ForeignKey(Track, on_delete=models.CASCADE, null=True)        # Foreign key to Track, nullable
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'TrackArtistJunction'

class AlbumArtistJunction(models.Model):
    junction_id = models.AutoField(primary_key=True)
    artist = models.ForeignKey('Artist', on_delete=models.CASCADE, null=True)    # Foreign key to Artist, nullable
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True)        # Foreign key to Album, nullable
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'AlbumArtistJunction'

class Artist(models.Model):
    artist_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    bio = models.TextField(null=True, blank=True)                                # bio is optional
    profile_image_url = models.CharField(max_length=512, null=True, blank=True)  # Allow profile_image_url to be nullable
    debut_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Artist'
