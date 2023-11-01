from .views import ClassificationView, ClusteringView
from django.urls import path
from . import views


urlpatterns = [
    
    path('', ClassificationView.as_view(), name="classification"),
    path('classification/', ClassificationView.as_view(), name="classification"),


    path('fileupload/', views.load_fileupload, name="fileupload"),
    path('process_fileupload/', views.process_fileupload, name="process_fileupload"),
    path('clustering/', ClusteringView.as_view(), name="clustering"),

    path('signout/', views.logout_and_clear_sessions, name="signout")
    
]