from django.shortcuts import render

# Create your views here.


def aboutusView(request):
    return render(request, "extras/aboutus.html")