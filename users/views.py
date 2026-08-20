from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
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
        UserService.register_user(self.request, form)
        messages.success(
            self.request,
            "Регистрация прошла успешно! На вашу почту отправлено письмо с ссылкой для подтверждения."
        )
        return super().form_valid(form)


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "users/login.html"

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active:
            messages.error(self.request, "Ваш email не подтверждён. Проверьте почту и перейдите по ссылке.")
            return redirect("users:login")
        messages.success(self.request, "Вы успешно вошли в систему!")
        return super().form_valid(form)


class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Вы вышли из системы.")
        return redirect("/")

    def post(self, request, *args, **kwargs):  # ← POST вместо GET
        logout(request)
        messages.success(request, "Вы вышли из системы.")
        return redirect("/")


class ActivateView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Ваш email подтверждён! Теперь вы можете войти.")
            return redirect("users:login")
        else:
            messages.error(request, "Ссылка недействительна или уже использована.")
            return redirect("users:login")