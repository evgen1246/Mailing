from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path
from .apps import UsersConfig
from . import views


app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
]
