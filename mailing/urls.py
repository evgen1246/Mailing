from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from .apps import MailingConfig
from .views import RecipientListView, RecipientCreateView, RecipientUpdateView, UserBlockView, UserListView, \
    MailingDisableView, StatisticsView, IndexView, MailingSendView, MailingDeleteView, MailingUpdateView, \
    MailingDetailView, MailingCreateView, MailingListView, MessageDeleteView, MessageUpdateView, MessageCreateView, \
    MessageListView, RecipientDeleteView

app_name = MailingConfig.name

urlpatterns = [
    # Получатели
    path("recipients/", RecipientListView.as_view(), name="recipient_list"),
    path("recipients/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path("recipients/<int:pk>/update/", RecipientUpdateView.as_view(), name="recipient_update"),
    path("recipients/<int:pk>/delete/", RecipientDeleteView.as_view(), name="recipient_delete"),
    # Сообщения
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path("messages/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"),
    path("messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),
    # Рассылки
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailings/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailings/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"),
    path("mailings/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),
    path("mailings/<int:pk>/send/", MailingSendView.as_view(), name="mailing_send"),
    #Главная
    path("", vary_on_cookie(cache_page(60 * 5)(IndexView.as_view())), name="index"),

    path("statistics/", StatisticsView.as_view(), name="statistics"),
    path("mailings/<int:pk>/disable/", MailingDisableView.as_view(), name="mailing_disable"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/block/", UserBlockView.as_view(), name="user_block"),
]
