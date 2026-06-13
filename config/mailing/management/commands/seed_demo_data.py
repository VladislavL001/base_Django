from datetime import timedelta

from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import Mailing, Message, Recipient


class Command(BaseCommand):
    help = 'Создает демонстрационных пользователей, получателей, сообщения и рассылки.'

    def handle(self, *args, **options):
        manager_group, _ = Group.objects.get_or_create(name='Managers')
        permissions = Permission.objects.filter(
            codename__in=['view_user', 'view_recipient', 'view_all_recipients', 'view_mailing', 'view_all_mailings', 'disable_mailing']
        )
        manager_group.permissions.set(permissions)

        manager, _ = User.objects.get_or_create(
            username='manager',
            defaults={'email': 'manager@example.com', 'is_staff': True, 'is_active': True},
        )
        manager.set_password('manager123')
        manager.is_staff = True
        manager.is_active = True
        manager.save()
        manager.groups.add(manager_group)

        user, _ = User.objects.get_or_create(
            username='user',
            defaults={'email': 'user@example.com', 'is_active': True},
        )
        user.set_password('user12345')
        user.is_active = True
        user.save()

        recipients = []
        for email, name in [
            ('anna@example.com', 'Анна Иванова'),
            ('petr@example.com', 'Петр Петров'),
            ('olga@example.com', 'Ольга Сидорова'),
        ]:
            recipient, _ = Recipient.objects.update_or_create(
                email=email,
                defaults={'full_name': name, 'comment': 'Демо-получатель', 'owner': user},
            )
            recipients.append(recipient)

        message, _ = Message.objects.update_or_create(
            subject='Демо-рассылка',
            owner=user,
            defaults={'body': 'Здравствуйте! Это демонстрационное письмо сервиса рассылок.'},
        )

        mailing, _ = Mailing.objects.update_or_create(
            message=message,
            owner=user,
            defaults={
                'start_time': timezone.now() + timedelta(minutes=1),
                'end_time': timezone.now() + timedelta(days=2),
                'is_enabled': True,
            },
        )
        mailing.recipients.set(recipients)

        self.stdout.write(self.style.SUCCESS('Демо-данные созданы. Логины: manager/manager123 и user/user12345.'))
