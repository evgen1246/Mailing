from django.core.management.base import BaseCommand

from mailing.models import Mailing
from mailing.services import send_mailing


class Command(BaseCommand):
    help = "Запустить рассылку по ID"

    def add_arguments(self, parser):
        parser.add_argument("mailing_id", type=int, help="ID рассылки")

    def handle(self, *args, **options):
        mailing_id = options["mailing_id"]

        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Рассылка #{mailing_id} не найдена"))
            return

        self.stdout.write(f"Запуск рассылки #{mailing_id} - {mailing.name}")
        result = send_mailing(mailing)

        if "error" in result:
            self.stdout.write(self.style.ERROR(result["error"]))
        else:
            self.stdout.write(self.style.SUCCESS(f"Успешно: {result['success']}"))
            self.stdout.write(self.style.ERROR(f"Ошибок: {result['failed']}"))
