from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image_filename = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user.username

class ListOfCrimes(models.Model):

    label_crime     = models.CharField(max_length=50, null=False, default=None)
    bg_color        = models.CharField(max_length=50, null=False, default=None)
    desc            = models.CharField(max_length=500, null=False, default=None)

    def __str__(self):
        return self.label_crime
