from django.db import models

class UserData(models.Model):
    user_id = models.IntegerField(primary_key=True)  # Specify user_id as the primary key
    name = models.TextField()
    email = models.TextField()
    password = models.TextField()
    display_name = models.TextField()
    role = models.BigIntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False  # Prevent Django from modifying the table
        db_table = 'UserData'  # Ensure this matches the name of your table
