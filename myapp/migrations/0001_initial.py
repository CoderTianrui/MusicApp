# Generated by Django 5.1.1 on 2024-10-12 10:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('user_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('email', models.TextField()),
                ('password', models.TextField()),
                ('display_name', models.TextField()),
                ('role', models.BigIntegerField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('last_login', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'UserData',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Album',
            fields=[
                ('album_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('release_date', models.DateField()),
                ('cover_image', models.CharField(max_length=255)),
                ('label', models.CharField(max_length=255)),
                ('album_type', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'Album',
            },
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('artist_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('profile_image', models.CharField(blank=True, max_length=255, null=True)),
                ('debut_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'Artist',
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('genre_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'Genre',
            },
        ),
        migrations.CreateModel(
            name='IpBanList',
            fields=[
                ('ban_id', models.AutoField(primary_key=True, serialize=False)),
                ('ip_address', models.CharField(max_length=255)),
                ('reason', models.TextField()),
                ('banned_at', models.DateTimeField()),
                ('revoked', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'IpBanList',
            },
        ),
        migrations.CreateModel(
            name='ManagementSetting',
            fields=[
                ('manage_setting_id', models.AutoField(primary_key=True, serialize=False)),
                ('setting_key', models.CharField(max_length=255)),
                ('setting_value', models.CharField(max_length=512)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'ManagementSetting',
            },
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('track_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('duration', models.IntegerField()),
                ('resource_link', models.CharField(max_length=512)),
                ('release_date', models.DateField()),
                ('lyrics', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'Track',
            },
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('log_id', models.AutoField(primary_key=True, serialize=False)),
                ('activity_type', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.userdata')),
            ],
            options={
                'db_table': 'ActivityLog',
            },
        ),
        migrations.CreateModel(
            name='AlbumArtistJunction',
            fields=[
                ('junction_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.album')),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.artist')),
            ],
            options={
                'db_table': 'AlbumArtistJunction',
            },
        ),
        migrations.AddField(
            model_name='album',
            name='artist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.artist'),
        ),
        migrations.CreateModel(
            name='KeyboardShortcut',
            fields=[
                ('shortcut_id', models.AutoField(primary_key=True, serialize=False)),
                ('action', models.CharField(max_length=255)),
                ('key_combination', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.userdata')),
            ],
            options={
                'db_table': 'KeyboardShortcut',
            },
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('playlist_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.userdata')),
            ],
            options={
                'db_table': 'Playlist',
            },
        ),
        migrations.CreateModel(
            name='SharedPlaylist',
            fields=[
                ('share_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.playlist')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.userdata')),
            ],
            options={
                'db_table': 'SharedPlaylist',
            },
        ),
        migrations.CreateModel(
            name='PlaylistTrack',
            fields=[
                ('playlist_track_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.playlist')),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.track')),
            ],
            options={
                'db_table': 'PlaylistTrack',
            },
        ),
        migrations.CreateModel(
            name='TrackAlbumJunction',
            fields=[
                ('junction_id', models.AutoField(primary_key=True, serialize=False)),
                ('track_number', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.album')),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.track')),
            ],
            options={
                'db_table': 'TrackAlbumJunction',
            },
        ),
        migrations.CreateModel(
            name='TrackArtistJunction',
            fields=[
                ('junction_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.artist')),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.track')),
            ],
            options={
                'db_table': 'TrackArtistJunction',
            },
        ),
        migrations.CreateModel(
            name='TrackGenreJunction',
            fields=[
                ('junction_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.genre')),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.track')),
            ],
            options={
                'db_table': 'TrackGenreJunction',
            },
        ),
        migrations.CreateModel(
            name='UserPlayHistory',
            fields=[
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.track')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.userdata')),
            ],
            options={
                'db_table': 'UserPlayHistory',
            },
        ),
        migrations.CreateModel(
            name='UserSetting',
            fields=[
                ('setting_id', models.AutoField(primary_key=True, serialize=False)),
                ('audio_quality_setting', models.CharField(max_length=255)),
                ('darkmode_setting', models.BooleanField(default=False)),
                ('dynamic_color_setting', models.BooleanField(default=False)),
                ('keyboard_shortcut', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.userdata')),
            ],
            options={
                'db_table': 'UserSetting',
            },
        ),
    ]
