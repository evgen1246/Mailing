from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from users.models import User

from .forms import MailingForm, MessageForm, RecipientForm
from .mixins import OwnerQuerysetMixin, OwnerRequiredMixin
from .models import Mailing, Message, Recipient
from .services import send_mailing

# Получатели


class RecipientListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Recipient
    template_name = "mailing/recipient_list.html"
    context_object_name = "recipients"


class RecipientCreateView(LoginRequiredMixin, OwnerQuerysetMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipient_list")


class RecipientDetailView(LoginRequiredMixin, OwnerQuerysetMixin, DetailView):
    model = Recipient
    template_name = "mailing/recipient_detail.html"
    context_object_name = "recipient"


class RecipientUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipient_list")


class RecipientDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Recipient
    template_name = "mailing/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")


# Сообщения


class MessageListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"


class MessageCreateView(LoginRequiredMixin, OwnerQuerysetMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageDetailView(LoginRequiredMixin, OwnerQuerysetMixin, DetailView):
    model = Message
    template_name = "mailing/message_detail.html"
    context_object_name = "message"


class MessageUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")


# Рассылки


class MailingListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"


class MailingDetailView(LoginRequiredMixin, OwnerQuerysetMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(LoginRequiredMixin, OwnerQuerysetMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")


class MailingUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")


class MailingDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingSendView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    """Запуск рассылки вручную (только владелец)"""

    model = Mailing
    template_name = "mailing/mailing_confirm_send.html"
    context_object_name = "mailing"

    def post(self, request, *args, **kwargs):
        mailing = self.get_object()
        result = send_mailing(mailing)

        if "error" in result:
            messages.error(request, result["error"])
        else:
            messages.success(request, f"Рассылка отправлена! Успешно: {result['success']}, Ошибок: {result['failed']}")
            if result["errors"]:
                for error in result["errors"][:3]:
                    messages.warning(request, error)

        return redirect("mailing:mailing_detail", pk=mailing.pk)


# Отключение рассылки (менеджер)


class MailingDisableView(LoginRequiredMixin, UpdateView):
    """Отключение рассылки (только для менеджеров)"""

    model = Mailing
    fields = []
    template_name = "mailing/mailing_confirm_disable.html"
    context_object_name = "mailing"
    success_url = reverse_lazy("mailing:mailing_list")

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.groups.filter(name="Менеджеры").exists()):
            messages.error(request, "У вас нет прав для этого действия.")
            return redirect("mailing:mailing_list")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_disabled = not self.object.is_disabled
        self.object.save()

        status = "отключена" if self.object.is_disabled else "включена"
        messages.success(request, f"Рассылка '{self.object.name}' {status}.")
        return redirect("mailing:mailing_list")


# Главная страница
class IndexView(LoginRequiredMixin, TemplateView):
    """Главная страница со статистикой"""

    template_name = "mailing/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        cache_key = f"stats_{user.id}"
        stats = cache.get(cache_key)

        if stats is None:
            now = timezone.now()
            if user.is_superuser or user.groups.filter(name="Менеджеры").exists():
                mailings = Mailing.objects.all()
                recipients = Recipient.objects.all()
            else:
                mailings = Mailing.objects.filter(owner=user)
                recipients = Recipient.objects.filter(owner=user)

            stats = {
                "total_mailings": mailings.count(),
                "active_mailings": mailings.filter(start_time__lte=now, end_time__gte=now, status="started").count(),
                "total_recipients": recipients.count(),
                "completed_mailings": mailings.filter(status="completed").count(),
                "created_mailings": mailings.filter(status="created").count(),
                "recent_mailings": mailings.order_by("-created_at")[:5],
            }
            cache.set(cache_key, stats, 60 * 5)

        context.update(stats)
        return context


# Статистика
class StatisticsView(LoginRequiredMixin, TemplateView):
    """Страница со статистикой"""

    template_name = "mailing/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .services import StatisticsService

        stats = StatisticsService.get_user_statistics(self.request.user)
        context["stats"] = stats
        return context


class UserListView(LoginRequiredMixin, ListView):
    """Список пользователей (только для менеджеров)"""

    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    ordering = ["-date_joined"]

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.groups.filter(name="Менеджеры").exists()):
            messages.error(request, "У вас нет прав для этого действия.")
            return redirect("mailing:index")
        return super().dispatch(request, *args, **kwargs)


class UserBlockView(LoginRequiredMixin, UpdateView):
    """Блокировка/разблокировка пользователя (только для менеджеров)"""

    model = User
    fields = []
    template_name = "users/user_confirm_block.html"
    context_object_name = "user"
    success_url = reverse_lazy("users:user_list")

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.groups.filter(name="Менеджеры").exists()):
            messages.error(request, "У вас нет прав для этого действия.")
            return redirect("mailing:index")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object == request.user:
            messages.error(request, "Вы не можете заблокировать себя.")
            return redirect("users:user_list")

        self.object.is_blocked = not self.object.is_blocked
        self.object.save()

        status = "заблокирован" if self.object.is_blocked else "разблокирован"
        messages.success(request, f"Пользователь {self.object.email} {status}.")
        return redirect("users:user_list")

