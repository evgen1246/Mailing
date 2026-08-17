from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """ Кастомная модель пользователя"""
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Введите электронную почту"
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        verbose_name="Аватар",
        blank=True,
        null=True
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
        blank=True,
        null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email


