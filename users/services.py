from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail


class UserService:
    """Сервис для работы с пользователями"""

    @staticmethod
    def register_user(request, form):
        """Регистрация пользователя"""
        user = form.save()

        # Отправка приветственного письма
        UserService._send_welcome_email(user)

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
