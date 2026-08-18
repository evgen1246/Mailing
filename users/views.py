from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomAuthenticationForm, CustomUserCreationForm
from .models import User
from .services import UserService


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = UserService.register_user(self.request, form)

        messages.success(self.request, "Регистрация прошла успешно! На вашу почту отправлено приветственное письмо.")
        return super().form_valid(form)


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "users/login.html"

    def form_valid(self, form):
        email = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = UserService.login_user(self.request, email, password)

        if user:
            messages.success(self.request, "Вы успешно вошли в систему!")
        else:
            messages.error(self.request, "Неверный email или пароль.")
            return super().form_invalid(form)

        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    next_page = "/"

    def get(self, request, *args, **kwargs):
        messages.success(request, "Вы вышли из системы.")
        return super().get(request, *args, **kwargs)
