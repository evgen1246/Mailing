from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetDoneView, PasswordResetView, \
    PasswordResetCompleteView
from django.urls import path, reverse_lazy

from mailing.views import UserBlockView, UserListView

from . import views
from .apps import UsersConfig
from .views import ActivateView, RegisterView, CustomLogoutView, CustomLoginView

app_name = UsersConfig.name

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("activate/<uidb64>/<token>/", ActivateView.as_view(), name="activate"),
    path(
        "password-reset/",
        PasswordResetView.as_view(
            template_name="users/password_reset_form.html",
            email_template_name="users/password_reset_email.html",
            success_url=reverse_lazy("users:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/complete/",
        PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/block/", UserBlockView.as_view(), name="user_block"),
]
