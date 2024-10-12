from django.core.management.base import BaseCommand
from myapp.models import UserData, Album, Track, Genre, Playlist, IpBanList

class Command(BaseCommand):
    help = 'Populates the database with mock data'

    def handle(self, *args, **kwargs):
        # Create mock users
        user1 = UserData.objects.create(
            name="John Doe",
            email="johndoe@example.com",
            password="password123",  # Normally, you'd hash this
            display_name="John",
            role=1
        )
        user2 = UserData.objects.create(
            name="Jane Smith",
            email="janesmith@example.com",
            password="password123",
            display_name="Jane",
            role=2
        )

        # Create some genres
        genre1 = Genre.objects.create(name="Rock", description="Rock genre")
        genre2 = Genre.objects.create(name="Jazz", description="Jazz genre")

        # Create mock albums
        album1 = Album.objects.create(
            title="Greatest Hits",
            release_date="2023-10-01",
            label="Awesome Music",
            total_tracks=12,
            description="A collection of the best hits."
        )

        album2 = Album.objects.create(
            title="Smooth Jazz",
            release_date="2022-08-15",
            label="Smooth Records",
            total_tracks=10,
            description="Relaxing jazz tunes."
        )

        # Create some tracks
        track1 = Track.objects.create(
            title="Hit Song 1",
            duration=180,
            resource_link="https://example.com/track1",
            release_date="2023-09-15"
        )

        track2 = Track.objects.create(
            title="Jazz Tune",
            duration=240,
            resource_link="https://example.com/jazztune",
            release_date="2022-08-10"
        )

        # Create some playlists
        playlist1 = Playlist.objects.create(
            owner=user1,
        )

        playlist2 = Playlist.objects.create(
            owner=user2,
        )

        # Add some IP bans
        IpBanList.objects.create(
            ip_address="192.168.1.1",
            user=user1,
            reason="Spamming",
            banned_at="2024-10-01"
        )

        self.stdout.write(self.style.SUCCESS('Mock data added successfully!'))
