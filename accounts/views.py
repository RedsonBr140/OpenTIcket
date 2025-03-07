from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

# Create your views here.

from django.utils.translation import gettext as _
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegistrationForm, UserProfileForm


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("home"))
        return render(request, "registration/login.html")

    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]
        remember_me = request.POST.get("remember_me")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            if remember_me:
                request.session.set_expiry(60 * 60 * 24 * 30)  # Expire in 30 days.
            else:
                request.session.set_expiry(0)  # Expire once the browser is closed.

            next_url = request.GET.get(
                "next", reverse("home")
            )  # If there's a next parameter redirect to there. If not, redirect to the homepage.
            return HttpResponseRedirect(next_url)
        else:
            return render(
                request,
                "registration/login.html",
                {
                    "error": _(
                        "Please enter a valid username and password. Note that all the fields are case sensitive."
                    )
                },
            )


class LogoutView(View):
    def get(self, request):
        logout(request)
        return render(request, "registration/logout.html")


class RegisterView(View):
    def get(self, request):
        return render(request, "registration/register.html")

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
        return render(request, "registration/register.html", {"form": form})


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        form = UserProfileForm(instance=request.user)
        return render(request, "registration/profile.html", {"form": form})

    def post(self, request):
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
        return render(request, "registration/profile.html", {"form": form})
