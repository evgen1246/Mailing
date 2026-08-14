from django.db import models


class Recipient(models.Model):
    """
    Модель получателя рассылки
    """
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
    """
    Модель сообщения для рассылки
    """
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
        ("draft", "Черновик"),
        ("sent", "Отправлена"),
        ("failed", "Ошибка"),
    ]

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
        default="draft",
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
        return self.name
