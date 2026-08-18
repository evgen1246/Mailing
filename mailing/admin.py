from django.contrib import admin

from .models import Mailing, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name", "created_at")
    list_display_links = ("id", "email")
    list_filter = ("created_at",)
    search_fields = ("email", "full_name", "comment")
    ordering = ("-created_at",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "created_at")
    list_display_links = ("id", "subject")
    search_fields = ("subject", "body")
    ordering = ("-created_at",)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "created_at", "sent_at")
    list_display_links = ("id", "name")
    list_filter = ("status", "created_at")
    search_fields = ("name",)
    filter_horizontal = ("recipients",)
    ordering = ("-created_at",)
