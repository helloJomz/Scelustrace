from .views import ClassificationView, AnalyticsView
from django.urls import path
from . import views


urlpatterns = [
    
    path('', ClassificationView.as_view(), name="classification"),
    path('classification/', ClassificationView.as_view(), name="classification"),

    path('admin/', views.account_management, name="account_management"),
    path('admin/account_management', views.account_management, name="account_management"),
    path('admin/activity_logs', views.activity_logs, name="activity_logs"),

    path('admin/load_user_table/', views.load_user_table, name="load_user_table"),
    path('admin/search_user_table/', views.search_user_table, name="search_user_table"),
    path('admin/del_user/', views.del_user, name="del_user"),

    path('analytics/', AnalyticsView.as_view(), name="analytics"),
    path('analytics/load_bubble/', views.load_bubble, name="bubble"),
    path('analytics/load_heatmap/', views.load_heatmap, name="heatmap"),
    path('analytics/load_marker/', views.load_marker, name="marker"),
    path('analytics/load_crime_analytics/', views.load_crime_analytics, name="crime_analytics"),
    path('analytics/load_crime_index/', views.load_crime_index, name="load_crime_index"),

    path('signout/', views.logout_and_clear_sessions, name="signout"),
    
]