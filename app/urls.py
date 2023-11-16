from .views import ClassificationView, AnalyticsView, RevampView
from django.urls import path
from . import views


urlpatterns = [
    
    path('', ClassificationView.as_view(), name="classification"),
    path('classification/', ClassificationView.as_view(), name="classification"),

    path('revamp/', RevampView.as_view(), name="revamp"),
    path('revamp/load_user_table/', views.load_user_table, name="load_user_table"),
    path('revamp/search_user_table/', views.search_user_table, name="search_user_table"),
    path('revamp/del_user/', views.del_user, name="del_user"),

    path('analytics/', AnalyticsView.as_view(), name="analytics"),
    path('analytics/load_bubble/', views.load_bubble, name="bubble"),
    path('analytics/load_heatmap/', views.load_heatmap, name="heatmap"),
    path('analytics/load_marker/', views.load_marker, name="marker"),
    path('analytics/load_crime_analytics/', views.load_crime_analytics, name="crime_analytics"),
    path('analytics/load_crime_index/', views.load_crime_index, name="load_crime_index"),

    path('signout/', views.logout_and_clear_sessions, name="signout"),
    
]