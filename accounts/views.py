from django.shortcuts import redirect, render
from django.http import HttpResponse
# Create your views here.

from django.utils.translation import gettext as _
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import RegistrationForm

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        remember_me = request.POST.get("remember_me")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            if remember_me:
                request.session.set_expiry(60 * 60 * 24 * 30) # Expire in 30 days.
            else:
                request.session.set_expiry(0) # Expire once the browser is closed.

            next_url = request.GET.get('next', reverse('home')) # If there's a next parameter redirect to there. If not, redirect to the homepage.
            return HttpResponseRedirect(next_url)
        else:
            return render(request, 'registration/login.html', {'error': _('Please enter a valid username and password. Note that all the fields are case sensitive.')})
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return render(request, "registration/logout.html")

def register_view(request):
    args = {}
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = RegistrationForm(initial={
            'first_name': '',
            'last_name': '',
            'username': '',
            'email': ''
        })
    args['form'] = form

    return render(request, 'registration/register.html', args)