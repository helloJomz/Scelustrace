from django.shortcuts import render, redirect
from app.models import ListOfCrimes

# Create your views here.


def aboutusView(request):

    list_of_crimes = ListOfCrimes.objects.all()

    if request.user.is_authenticated:
        return render(request, 'app/classification.html', context={'data':list_of_crimes})
    elif not request.user.is_authenticated and not request.path_info.startswith('/aboutus'):
        return redirect('aboutus')
    else:
        return render(request, "extras/aboutus.html", context={'data':list_of_crimes})
    
