from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Mailing, MailingAttempt


class MailingUnavailableError(ValueError):
    pass


def send_mailing(mailing):
    mailing.refresh_status()
    if not mailing.can_send():
        raise MailingUnavailableError(
            'Рассылку можно запускать только во включенном состоянии и в период между датой начала и датой окончания.'
        )

    recipients = list(mailing.recipients.all())
    if not recipients:
        raise MailingUnavailableError('У рассылки нет получателей.')

    result = {'success': 0, 'failure': 0, 'total': len(recipients)}
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)

    for recipient in recipients:
        try:
            sent_count = send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=from_email,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            if sent_count:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status=MailingAttempt.SUCCESS,
                    server_response=f'Письмо отправлено в {timezone.now():%Y-%m-%d %H:%M:%S %Z}',
                )
                result['success'] += 1
            else:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status=MailingAttempt.FAILURE,
                    server_response='Почтовый сервер вернул 0 отправленных писем.',
                )
                result['failure'] += 1
        except Exception as exc:
            MailingAttempt.objects.create(
                mailing=mailing,
                recipient=recipient,
                status=MailingAttempt.FAILURE,
                server_response=str(exc),
            )
            result['failure'] += 1

    return result
