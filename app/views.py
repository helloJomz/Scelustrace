from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.sessions.models import Session
# Create your views here.


class ClassificationView(View):
    def get(self, request):
        return render(request, 'app/classification.html')

    def post(self, request):
        pass


def logout_and_clear_sessions(request):
    auth.logout(request)  # Logout the user
    request.session.flush()  # Clear all sessions
    return redirect('/login')
