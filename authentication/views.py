from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
from app.models import UserProfile
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

import random


# Create your views here.
class SignupView(View):
    def get(self, request):
        validator = request.session.get('user_fullname')
        prev_page = request.session.get('prev_page')
        if validator:
            if prev_page:
                return redirect(prev_page)
            else:
                return redirect('classification')
        else:
            return render(request, "authentication/signup.html")
            
    
    def post(self, request):
        username    = request.POST.get('username', '')
        password    = request.POST.get('password', '')
        firstname   = request.POST.get('firstname', '')
        lastname    = request.POST.get('lastname', '')

        unique_digits = random.randint(1, 10)

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "fieldName": "username",
                "error": "Username already exists."
            })
        
        else:
            
            # Create a new user
            user = User(username = username, first_name = firstname, last_name = lastname)
            user.set_password(password)
            user.save()

            # Create a UserProfile for the new user
            user_profile = UserProfile(user=user)
            filename = str(unique_digits) + ".png"
            user_profile.profile_image_filename = filename
            user_profile.save()

            return JsonResponse({
                "location": "login/",
            })
        
class LoginView(View):
    def get(self, request):
        validator = request.session.get('user_fullname')
        prev_page = request.session.get('prev_page')
        if validator:
            if prev_page:
                return redirect(prev_page)
            else:
                return redirect('classification')
        else:
            return render(request, "authentication/login.html")
            
    
    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user:
            # Authentication successful, you can filter UserProfile based on the user's id
            user_profile = UserProfile.objects.filter(user=user.id).first()

            if user.is_staff == False:
                login(request, user)  
                request.session["user_fullname"] = user.first_name + " " + user.last_name
                request.session["status"] = False
                request.session["profile_img"] = user_profile.profile_image_filename if user_profile and user_profile.profile_image_filename else False
                return JsonResponse({"location": "app/classification", "login_status": True})
            else:
                login(request, user)  
                request.session["user_fullname"] = user.first_name + " " + user.last_name
                request.session["status"] = True
                request.session["profile_img"] = user_profile.profile_image_filename if user_profile and user_profile.profile_image_filename else False
                return JsonResponse({"location": "app/classification", "login_status": True})
        else:
            return JsonResponse({"login_status": False,
                                    "msg": "Username or Password is incorrect."})
    