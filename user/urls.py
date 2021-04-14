from django.urls import include, path

from . import views

app_name = "user"
urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit", views.edit_profile, name="edit_profile"),
    path(
        "profile/change_password/",
        views.change_password,
        name="change_password",
    ),
]
