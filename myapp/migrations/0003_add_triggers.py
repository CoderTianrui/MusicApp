from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_alter_userdata_options_remove_album_album_type_and_more'),
    ]

    operations = [
        # ActivityLog trigger: record the CRUD operations of UserData table
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION log_user_activity()
            RETURNS TRIGGER AS $$
            BEGIN
                IF TG_OP = 'INSERT' THEN
                    INSERT INTO "ActivityLog" (user_id, activity_type, created_at) 
                    VALUES (NEW.user_id, 'INSERT', NOW());
                    RETURN NEW;
                ELSIF TG_OP = 'UPDATE' THEN
                    INSERT INTO "ActivityLog" (user_id, activity_type, created_at) 
                    VALUES (NEW.user_id, 'UPDATE', NOW());
                    RETURN NEW;
                END IF;
                RETURN NULL;  -- For DELETE, just return NULL without logging to avoid conflicts
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER user_activity_trigger
            AFTER INSERT OR UPDATE ON "UserData"
            FOR EACH ROW EXECUTE FUNCTION log_user_activity();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS user_activity_trigger ON "UserData";
            DROP FUNCTION IF EXISTS log_user_activity();
            """
        ),

        # Album trigger: when doing CRUD in TrackAlbumJunction, update "total_tracks" in Album
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION update_total_tracks()
            RETURNS TRIGGER AS $$
            BEGIN
                IF TG_OP = 'INSERT' THEN
                    UPDATE "Album"
                    SET total_tracks = (SELECT COUNT(*) FROM "TrackAlbumJunction" 
                    WHERE album_id = NEW.album_id)
                    WHERE album_id = NEW.album_id;
                    RETURN NEW;
                ELSIF TG_OP = 'DELETE' THEN
                    UPDATE "Album"
                    SET total_tracks = (SELECT COUNT(*) FROM "TrackAlbumJunction" 
                    WHERE album_id = OLD.album_id)
                    WHERE album_id = OLD.album_id;
                    RETURN OLD;
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER update_total_tracks_trigger
            AFTER INSERT OR DELETE ON "TrackAlbumJunction"
            FOR EACH ROW EXECUTE FUNCTION update_total_tracks();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS update_total_tracks_trigger ON "TrackAlbumJunction";
            DROP FUNCTION IF EXISTS update_total_tracks();
            """
        )
    ]
