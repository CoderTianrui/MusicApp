# Generated by Django 5.1.1 on 2024-10-12 11:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userdata',
            options={},
        ),
        migrations.RemoveField(
            model_name='album',
            name='album_type',
        ),
        migrations.RemoveField(
            model_name='album',
            name='artist',
        ),
        migrations.RemoveField(
            model_name='album',
            name='cover_image',
        ),
        migrations.RemoveField(
            model_name='artist',
            name='profile_image',
        ),
        migrations.AddField(
            model_name='album',
            name='cover_image_url',
            field=models.CharField(default='https://example.com/default_cover_image.jpg', max_length=512),
        ),
        migrations.AddField(
            model_name='album',
            name='total_tracks',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='profile_image_url',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='ipbanlist',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.userdata'),
        ),
        migrations.AddField(
            model_name='managementsetting',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='activitylog',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.userdata'),
        ),
        migrations.AlterField(
            model_name='albumartistjunction',
            name='album',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.album'),
        ),
        migrations.AlterField(
            model_name='albumartistjunction',
            name='artist',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.artist'),
        ),
        migrations.AlterField(
            model_name='keyboardshortcut',
            name='key_combination',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='keyboardshortcut',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.userdata'),
        ),
        migrations.AlterField(
            model_name='playlist',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.userdata'),
        ),
        migrations.AlterField(
            model_name='playlisttrack',
            name='playlist',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.playlist'),
        ),
        migrations.AlterField(
            model_name='playlisttrack',
            name='track',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.track'),
        ),
        migrations.AlterField(
            model_name='sharedplaylist',
            name='playlist',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.playlist'),
        ),
        migrations.AlterField(
            model_name='sharedplaylist',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.userdata'),
        ),
        migrations.AlterField(
            model_name='trackalbumjunction',
            name='album',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.album'),
        ),
        migrations.AlterField(
            model_name='trackalbumjunction',
            name='track',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.track'),
        ),
        migrations.AlterField(
            model_name='trackartistjunction',
            name='artist',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.artist'),
        ),
        migrations.AlterField(
            model_name='trackartistjunction',
            name='track',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.track'),
        ),
        migrations.AlterField(
            model_name='trackgenrejunction',
            name='genre',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.genre'),
        ),
        migrations.AlterField(
            model_name='trackgenrejunction',
            name='track',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.track'),
        ),
        migrations.AlterField(
            model_name='userplayhistory',
            name='track',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.track'),
        ),
        migrations.AlterField(
            model_name='userplayhistory',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.userdata'),
        ),
        migrations.AlterField(
            model_name='usersetting',
            name='audio_quality_setting',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='usersetting',
            name='darkmode_setting',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='usersetting',
            name='dynamic_color_setting',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='usersetting',
            name='keyboard_shortcut',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='usersetting',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.userdata'),
        ),
    ]
