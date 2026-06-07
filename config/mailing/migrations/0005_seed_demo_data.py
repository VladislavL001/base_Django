# Generated manually to provide initial demo data for the mailing service.

from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.utils import timezone


def create_demo_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')
    Recipient = apps.get_model('mailing', 'Recipient')
    Message = apps.get_model('mailing', 'Message')
    Mailing = apps.get_model('mailing', 'Mailing')

    manager_group, _ = Group.objects.get_or_create(name='Managers')

    manager, _ = User.objects.update_or_create(
        username='manager',
        defaults={
            'email': 'manager@example.com',
            'password': make_password('manager123'),
            'is_staff': True,
            'is_active': True,
        },
    )
    manager.groups.add(manager_group)

    user, _ = User.objects.update_or_create(
        username='user',
        defaults={
            'email': 'user@example.com',
            'password': make_password('user12345'),
            'is_active': True,
        },
    )

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
            'status': 'Создана',
            'is_enabled': True,
        },
    )
    mailing.recipients.set(recipients)


def reverse_demo_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Recipient = apps.get_model('mailing', 'Recipient')
    Message = apps.get_model('mailing', 'Message')

    Recipient.objects.filter(email__in=['anna@example.com', 'petr@example.com', 'olga@example.com']).delete()
    Message.objects.filter(subject='Демо-рассылка').delete()
    User.objects.filter(username__in=['manager', 'user']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0004_ownership_attempts_enabled'),
    ]

    operations = [
        migrations.RunPython(create_demo_data, reverse_demo_data),
    ]
