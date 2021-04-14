from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from .forms import ProfileForm, UserForm
from .models import Doctor, Profile, User


def register(request):
    if request.method != "POST":
        user_form = UserForm()
        profile_form = ProfileForm()
    else:
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = Profile(
                user=user,
                birth_date=request.POST["birth_date"],
                city=request.POST["city"],
                phone_number=request.POST["phone_number"],
            )
            profile.save()
            return redirect("user:login")
    messages.error(request, "Error")
    context = {"user_form": user_form, "profile_form": profile_form}
    return render(request, "registration/register.html", context)


@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user.id)
    return render(request, "registration/profile.html", {"profile": profile})


@login_required
def edit_profile(request):
    profile = Profile.objects.get(user=request.user.id)
    form = ProfileForm(request.POST or None, instance=profile)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("user:profile")
    return render(request, "registration/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request, "Your password was successfully updated!"
            )
            return redirect("user:profile")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "registration/change_password.html", {"form": form})
