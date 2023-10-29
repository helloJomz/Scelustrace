from django.db import models

# Create your models here.

class ListOfCrimes(models.Model):

    label_crime     = models.CharField(max_length=50, null=False, default=None)
    bg_color        = models.CharField(max_length=50, null=False, default=None)
    desc            = models.CharField(max_length=500, null=False, default=None)

    def __str__(self):
        return self.label_crime
