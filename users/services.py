from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class UserService:
    """Сервис для работы с пользователями"""

    @staticmethod
    def register_user(request, form):
        """
        Регистрация пользователя с отправкой письма для подтверждения email
        """
        user = form.save(commit=False)
        user.is_active = False  # Пользователь неактивен до подтверждения
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_url = request.build_absolute_uri(
            reverse(
                "users:activate",
                kwargs={"uidb64": uid, "token": token},
            )
        )

        send_mail(
            subject="Подтверждение регистрации",
            message=f"""
    Здравствуйте!

    Для подтверждения регистрации на сайте перейдите по ссылке:
    {activation_url}

    Если вы не регистрировались, проигнорируйте это письмо.

    С уважением,
    Команда сервиса рассылок
                """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return user

    @staticmethod
    def _send_welcome_email(user):
        """Отправка приветственного письма пользователю"""
        try:
            send_mail(
                subject="Добро пожаловать в сервис рассылок!",
                message=f"""
Здравствуйте, {user.email}!

Вы успешно зарегистрировались в сервисе.

Теперь вы можете:
- Создавать и управлять рассылками
- Добавлять получателей
- Отслеживать статистику отправок

С уважением,
Команда сервиса рассылок
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Ошибка отправки письма: {e}")

    @staticmethod
    def login_user(request, email, password):
        """Авторизация пользователя по email и паролю"""
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return user
        return None
