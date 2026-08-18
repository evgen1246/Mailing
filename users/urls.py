from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
]
