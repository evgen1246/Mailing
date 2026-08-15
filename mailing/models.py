from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Recipient(models.Model):
    """Модель получателя рассылки"""
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Введите email получателя"
    )
    full_name = models.CharField(
        max_length=255,
        verbose_name="Ф.И.О.",
        help_text="Введите Ф.И.О. получателя"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий",
        help_text="Введите комментарий (необязательно)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Message(models.Model):
    """Модель сообщения для рассылки"""
    subject = models.CharField(
        max_length=255,
        verbose_name="Тема письма",
        help_text="Введите тему письма"
    )
    body = models.TextField(
        verbose_name="Тело письма",
        help_text="Введите текст письма"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    """
    Модель рассылки
    """
    STATUS_CHOICES = [
        ("created", "Создана"),
        ("started", "Запущена"),
        ("completed", "Завершена"),
    ]
    start_time = models.DateTimeField(
        verbose_name="Дата и время начала отправки",
        help_text="Укажите дату и время начала рассылки"
    )
    end_time = models.DateTimeField(
        verbose_name="Дата и время окончания отправки",
        help_text="Укажите дату и время окончания рассылки"
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Название рассылки",
        help_text="Введите название рассылки"
    )
    recipients = models.ManyToManyField(
        Recipient,
        verbose_name="Получатели",
        help_text="Выберите получателей"
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        verbose_name="Сообщение",
        help_text="Выберите сообщение"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="created",
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    sent_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата отправки"
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Рассылка #{self.id} - {self.message.subject}"

    def clean(self):
        """Валидация модели"""
        errors = {}
        if self.start_time and self.start_time < timezone.now():
            errors['start_time'] = ValidationError(
                'Дата и время начала не могут быть в прошлом.'
            )

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            errors['end_time'] = ValidationError(
                'Дата и время окончания должны быть позже даты начала.'
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Переопределяем save для вызова валидации"""

        self.full_clean()
        super().save(*args, **kwargs)

    def update_status(self):
        """Обновляет статус рассылки на основе текущего времени."""
        now = timezone.now()
        new_status = None

        if now < self.start_time:
            new_status = "created"
        elif self.start_time <= now <= self.end_time:
            new_status = "started"  #
        else:
            new_status = "completed"

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])
            return True
        return False

    def get_status_display(self):
        """Возвращает читаемый статус"""
        status_map = dict(self.STATUS_CHOICES)
        return status_map.get(self.status, "Неизвестно")
