from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from app.models import ListOfCrimes


# Create your views here.
class SignupView(View):
    def get(self, request):
        return render(request, 'authentication/signup.html')
    
    def post(self, request):
        username    = request.POST.get('username', '')
        password    = request.POST.get('password', '')
        firstname   = request.POST.get('firstname', '')
        lastname    = request.POST.get('lastname', '')

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

            return JsonResponse({
                "location": "login/",
            })
        
class LoginView(View):
    def get(self, request):
        list_of_crimes = ListOfCrimes.objects.all()
        context = {'data': list_of_crimes}
        
        if request.user.is_authenticated:
            return render(request, 'app/classification.html', context)
        elif not request.user.is_authenticated and not request.path_info.startswith('/login'):
            return redirect('login')
        else:
            return render(request, 'authentication/login.html', context)
    
    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user:
            if user.is_staff == False:
                login(request, user)  
                request.session["user_fullname"] = user.first_name + " " + user.last_name
                request.session["status"] = False
                return JsonResponse({"location": "app/classification", "login_status": True})
            else:
                login(request, user)  
                request.session["user_fullname"] = user.first_name + " " + user.last_name
                request.session["status"] = True
                return JsonResponse({"location": "app/classification", "login_status": True})
        else:
            return JsonResponse({"login_status": False,
                                    "msg": "Username or Password is incorrect."})
    