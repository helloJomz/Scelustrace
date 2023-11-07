from .views import ClassificationView, ClusteringView, AnalyticsView
from django.urls import path
from . import views


urlpatterns = [
    
    path('', ClassificationView.as_view(), name="classification"),
    path('classification/', ClassificationView.as_view(), name="classification"),


    path('fileupload/', views.load_fileupload, name="fileupload"),
    path('process_fileupload/', views.process_fileupload, name="process_fileupload"),
    path('clustering/', ClusteringView.as_view(), name="clustering"),

    path('analytics/', AnalyticsView.as_view(), name="analytics"),
    path('analytics/load_bubble/', views.load_bubble, name="bubble"),
    path('analytics/load_heatmap/', views.load_heatmap, name="heatmap"),
    path('analytics/load_marker/', views.load_marker, name="marker"),

    path('signout/', views.logout_and_clear_sessions, name="signout"),
    
]