from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


class OwnerQuerysetMixin:
    """
    Миксин для фильтрации queryset по владельцу.
    Менеджеры видят все объекты, обычные пользователи — только свои.
    """

    manager_group = "Менеджеры"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return queryset
        if user.groups.filter(name=self.manager_group).exists():
            return queryset

        return queryset.filter(owner=user)

    def form_valid(self, form):
        """При создании объекта автоматически назначаем владельца"""
        if not form.instance.pk:
            form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь является владельцем объекта."""

    def test_func(self):
        obj = self.get_object()
        if self.request.user.is_superuser:
            return True
        return obj.owner_id == self.request.user.id

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет прав для этого действия.")
        return redirect("mailing:mailing_list")
