from django.contrib import admin
from .models import ListOfCrimes, UserProfile


# Register your models here.
admin.site.register(ListOfCrimes)
admin.site.register(UserProfile)
