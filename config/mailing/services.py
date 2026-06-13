from django.conf import settings
from django.core.mail import send_mail

from .models import Mailing, MailingAttempt


def send_mailing(mailing_id):
    mailing = Mailing.objects.get(pk=mailing_id)

    if not mailing.can_send():
        raise ValueError(
            'Рассылка недоступна для отправки'
        )

    if not mailing.is_active:
        raise ValueError(
            'Рассылка отключена менеджером'
        )

    recipients = mailing.recipients.all()

    for recipient in recipients:

        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[recipient.email],
                fail_silently=False,
            )

            MailingAttempt.objects.create(
                mailing=mailing,
                status=MailingAttempt.SUCCESS,
                server_response='Письмо отправлено'
            )

        except Exception as e:

            MailingAttempt.objects.create(
                mailing=mailing,
                status=MailingAttempt.FAILED,
                server_response=str(e)
            )