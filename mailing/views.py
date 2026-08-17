from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from .models import Recipient, Message, Mailing
from .forms import RecipientForm, MessageForm, MailingForm
from .services import send_mailing
from django.utils import timezone



#Получатели
class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = "mailing/recipient_list.html"
    context_object_name = "recipients"


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipient_list")


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipient_list")


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = "mailing/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")


#Сообщения

class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")


#Рассылки

class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingSendView(LoginRequiredMixin, DetailView):
    """Запуск рассылки вручную"""
    model = Mailing
    template_name = "mailing/mailing_confirm_send.html"
    context_object_name = "mailing"

    def post(self, request, *args, **kwargs):
        mailing = self.get_object()
        result = send_mailing(mailing)

        if "error" in result:
            messages.error(request, result["error"])
        else:
            messages.success(
                request,
                f"Рассылка отправлена! Успешно: {result['success']}, Ошибок: {result['failed']}"
            )
            if result["errors"]:
                for error in result["errors"][:3]:  # Показываем первые 3 ошибки
                    messages.warning(request, error)

        return redirect("mailing:mailing_detail", pk=mailing.pk)


class IndexView(LoginRequiredMixin, TemplateView):
    """Главная страница со статистикой"""
    template_name = "mailing/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()

        # Общее количество всех рассылок
        total_mailings = Mailing.objects.count()

        # Количество активных рассылок
        # Активная: текущая дата между start_time и end_time И статус "started"
        active_mailings = Mailing.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            status="started"
        ).count()

        # Количество уникальных получателей
        total_recipients = Recipient.objects.count()

        # Дополнительно: количество завершённых и созданных (для статистики)
        completed_mailings = Mailing.objects.filter(status="completed").count()
        created_mailings = Mailing.objects.filter(status="created").count()

        # Последние 5 рассылок (для отображения на главной)
        recent_mailings = Mailing.objects.order_by("-created_at")[:5]

        context.update({
            "total_mailings": total_mailings,
            "active_mailings": active_mailings,
            "total_recipients": total_recipients,
            "completed_mailings": completed_mailings,
            "created_mailings": created_mailings,
            "recent_mailings": recent_mailings,
            "now": now,
        })

        return context