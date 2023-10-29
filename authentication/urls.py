from .views import SignupView, LoginView
from django.urls import path
from . import views


urlpatterns = [

    path('', LoginView.as_view(), name="login"),
    path('login/', LoginView.as_view(), name="login"),
    path('signup/', SignupView.as_view(), name="signup"),

]