from django.db import models

# Create your models here.

class AuthUser(models.Model):
    firstname       = models.CharField(max_length=50)
    lastname        = models.CharField(max_length=50)
    username        = models.CharField(max_length=30)
    password        = models.CharField(max_length=150)
    datecreated     = models.DateField()
    is_staff        = models.BooleanField(default=False)

    def __str__(self):
        return self.username
