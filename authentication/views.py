from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
import json
from django.http import JsonResponse
from django.utils import timezone
from .models import AuthUser
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from django.contrib.auth import authenticate, login



# Create your views here.
class SignupView(View):
    def get(self, request):
        return render(request, 'authentication/signup.html')
    
    def post(self, request):
        username    = request.POST.get('username', '')
        password    = request.POST.get('password', '')
        firstname   = request.POST.get('firstname', '')
        lastname    = request.POST.get('lastname', '')
        currentdate = timezone.now().date()

        hashed_password = make_password(password)

        # Check if the username already exists
        if AuthUser.objects.filter(username=username).exists():
            return JsonResponse({
                "fieldName": "username",
                "error": "Username already exists."
            })
        else:
            
            auth_user = AuthUser(
                username=username,
                password=hashed_password,
                firstname=firstname,
                lastname=lastname,
                datecreated=currentdate
            )

            auth_user.save()

            return JsonResponse({
                "location": "login/",
            })
        
class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')
    
    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]

        user = AuthUser.objects.filter(username=username).first()

        if user:
            if check_password(password, user.password):  
                if user.is_staff == False:
                    request.session["user_fullname"] = user.firstname + " " + user.lastname
                    request.session["username"] = user.username
                    request.session["status"] = False
                    return JsonResponse({"location": "app/classification", "login_status": True})
                else:
                    request.session["user_fullname"] = user.firstname + " " + user.lastname
                    request.session["username"] = user.username
                    request.session["status"] = True
                    return JsonResponse({"location": "app/classification", "login_status": True})
            else:
               return JsonResponse({"login_status": False,
                                 "msg": "Username or Password is incorrect."})
        else:
            return JsonResponse({"login_status": False,
                                 "msg": "Username or Password is incorrect."})

        
    
class HomeView(View):
    def get(self, request):
        return render(request, 'authentication/home.html')
    
