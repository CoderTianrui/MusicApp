from django.contrib import admin
from .models import (
    UserData, ActivityLog, Playlist, SharedPlaylist, PlaylistTrack, UserPlayHistory,
    ManagementSetting, IpBanList, UserSetting, KeyboardShortcut, Track, TrackAlbumJunction,
    TrackGenreJunction, Genre, Album, TrackArtistJunction, AlbumArtistJunction, Artist
)

class UserDataAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'email', 'role', 'created_at', 'updated_at')
    search_fields = ('name', 'email')
    list_filter = ('role',)
    ordering = ('-created_at',)

class TrackAdmin(admin.ModelAdmin):
    list_display = ('track_id', 'title', 'duration', 'release_date', 'resource_link')
    search_fields = ('title', 'lyrics')
    list_filter = ('release_date',)
    ordering = ('-release_date',)

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('artist_id', 'name', 'debut_date', 'profile_image_url')
    search_fields = ('name', 'bio')
    list_filter = ('debut_date',)
    ordering = ('-debut_date',)

class AlbumAdmin(admin.ModelAdmin):
    list_display = ('album_id', 'title', 'release_date', 'label', 'total_tracks', 'cover_image_url')
    search_fields = ('title', 'label', 'description')
    list_filter = ('release_date',)
    ordering = ('-release_date',)

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('playlist_id', 'owner', 'created_at', 'updated_at')
    search_fields = ('owner__email',)
    ordering = ('-created_at',)

class PlaylistTrackInline(admin.TabularInline):
    model = PlaylistTrack
    extra = 1

class PlaylistAdmin(admin.ModelAdmin):
    inlines = [PlaylistTrackInline]
    list_display = ('playlist_id', 'owner', 'created_at', 'updated_at')
    search_fields = ('owner__email',)
    ordering = ('-created_at',)

class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('log_id', 'user', 'activity_type', 'created_at')
    search_fields = ('user__email', 'activity_type')
    list_filter = ('activity_type',)
    ordering = ('-created_at',)

class SharedPlaylistAdmin(admin.ModelAdmin):
    list_display = ('share_id', 'playlist', 'user', 'created_at')
    search_fields = ('playlist__playlist_id', 'user__email')
    ordering = ('-created_at',)

class UserPlayHistoryAdmin(admin.ModelAdmin):
    list_display = ('history_id', 'user', 'track', 'created_at')
    search_fields = ('user__email', 'track__title')
    ordering = ('-created_at',)

class ManagementSettingAdmin(admin.ModelAdmin):
    list_display = ('manage_setting_id', 'setting_key', 'setting_value', 'created_at', 'updated_at')
    search_fields = ('setting_key',)
    ordering = ('-created_at',)

class IpBanListAdmin(admin.ModelAdmin):
    list_display = ('ban_id', 'ip_address', 'user', 'reason', 'banned_at', 'revoked')
    search_fields = ('ip_address', 'user__email')
    list_filter = ('revoked',)
    ordering = ('-banned_at',)

admin.site.register(UserData, UserDataAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)
admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(SharedPlaylist, SharedPlaylistAdmin)
admin.site.register(PlaylistTrack)
admin.site.register(UserPlayHistory, UserPlayHistoryAdmin)
admin.site.register(ManagementSetting, ManagementSettingAdmin)
admin.site.register(IpBanList, IpBanListAdmin)
admin.site.register(UserSetting)
admin.site.register(KeyboardShortcut)
admin.site.register(Track, TrackAdmin)
admin.site.register(TrackAlbumJunction)
admin.site.register(TrackGenreJunction)
admin.site.register(Genre)
admin.site.register(Album, AlbumAdmin)
admin.site.register(TrackArtistJunction)
admin.site.register(AlbumArtistJunction)
admin.site.register(Artist, ArtistAdmin)

