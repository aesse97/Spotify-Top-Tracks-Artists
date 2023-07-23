from django.db import models
from django.contrib.auth.models import User

class SpotifyToken(models.Model):
    user_id = models.CharField(max_length=50, unique=True, default="defaultvalue")
    access_token = models.CharField(max_length=512)
    token_type = models.CharField(max_length=50)
    expires_in = models.IntegerField()
    refresh_token = models.CharField(max_length=255)
    scope = models.CharField(max_length=255, null=True)
    expires_at = models.DateTimeField(null=True)