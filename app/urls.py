from .views import ClassificationView
from django.urls import path
from . import views


urlpatterns = [
    
    path('', ClassificationView.as_view(), name="classification"),
    path('classification', ClassificationView.as_view(), name="classification"),
    path('signout', views.logout_and_clear_sessions, name="signout")
    
]