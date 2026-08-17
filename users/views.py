from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import User


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        response = super().form_valid(form)

        # Отправка приветственного письма
        try:
            send_mail(
                subject="Добро пожаловать!",
                message=f"Здравствуйте, {self.object.email}!\n\n"
                        f"Вы успешно зарегистрировались в сервисе рассылок.\n\n"
                        f"С уважением,\nКоманда проекта",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.object.email],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(self.request, "Регистрация прошла успешно! Войдите в систему.")
        return response


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "users/login.html"

    def form_valid(self, form):
        messages.success(self.request, "Вы успешно вошли!")
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        messages.success(request, "Вы вышли из системы.")
        return super().get(request, *args, **kwargs)
