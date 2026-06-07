from django.core.management.base import BaseCommand, CommandError

from mailing.models import Mailing
from mailing.services import MailingUnavailableError, send_mailing


class Command(BaseCommand):
    help = 'Ручной запуск рассылки по ID.'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки')

    def handle(self, *args, **options):
        mailing = Mailing.objects.filter(pk=options['mailing_id']).first()
        if mailing is None:
            raise CommandError('Рассылка не найдена.')
        try:
            result = send_mailing(mailing)
        except MailingUnavailableError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(
            self.style.SUCCESS(
                f"Рассылка выполнена: всего {result['total']}, успешно {result['success']}, не успешно {result['failure']}."
            )
        )
