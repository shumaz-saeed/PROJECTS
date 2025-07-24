

from django.db import models
from django.contrib.auth.models import User
class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    bio = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    provider = models.CharField(max_length=50 , blank=True, null=True)  
    profile_picture = models.URLField(blank=True, null=True)
    provider_id = models.CharField(max_length=255) 
    access_token = models.CharField(max_length=500, blank=True, null=True)
    refresh_token = models.CharField(max_length=500, blank=True, null=True)
    last_login_provider = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.provider})"

