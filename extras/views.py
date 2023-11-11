from django.shortcuts import render, redirect

# Create your views here.
def aboutusView(request):
    validator = request.session.get('user_fullname')
    prev_page = request.session.get('prev_page')
    if validator:
        if prev_page:
            return redirect(prev_page)
        else:
            return redirect('classification')
    else:
        return render(request, "extras/aboutus.html")