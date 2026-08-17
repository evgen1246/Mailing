from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import MailingAttempt


def send_mailing(mailing):
    """Отправляет рассылку всем получателям. Возвращает словарь со статистикой."""
    now = timezone.now()

    # Проверка: можно ли отправлять
    if now < mailing.start_time:
        return {"error": "Рассылка ещё не началась"}
    if now > mailing.end_time:
        return {"error": "Рассылка уже завершена"}

    recipients = mailing.recipients.all()
    if not recipients.exists():
        return {"error": "Нет получателей"}

    success_count = 0
    failed_count = 0
    errors = []

    for recipient in recipients:
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )

            MailingAttempt.objects.create(
                mailing=mailing,
                recipient=recipient,
                status="success",
                server_response="Письмо отправлено успешно"
            )
            success_count += 1

        except Exception as e:
            error_text = str(e)
            MailingAttempt.objects.create(
                mailing=mailing,
                recipient=recipient,
                status="failed",
                server_response=error_text
            )
            failed_count += 1
            errors.append(f"{recipient.email}: {error_text}")

    # Обновляем статус рассылки
    if success_count > 0:
        mailing.status = "started"
        mailing.save(update_fields=["status"])

    return {
        "success": success_count,
        "failed": failed_count,
        "errors": errors
    }