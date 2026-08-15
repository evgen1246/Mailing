from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import  DetailView
from .models import Mailing



class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj