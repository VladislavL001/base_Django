# Generated manually to add ownership, attempts, and mailing switches.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mailing', '0003_rename_date_first_mailing_end_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipient',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recipients', to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AddField(
            model_name='message',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AddField(
            model_name='mailing',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mailings', to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AddField(
            model_name='mailing',
            name='is_enabled',
            field=models.BooleanField(default=True, verbose_name='Включена'),
        ),
        migrations.AlterField(
            model_name='mailing',
            name='status',
            field=models.CharField(choices=[('Создана', 'Создана'), ('Запущена', 'Запущена'), ('Завершена', 'Завершена')], default='Создана', max_length=20, verbose_name='Статус'),
        ),
        migrations.CreateModel(
            name='MailingAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attempt_time', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки')),
                ('status', models.CharField(choices=[('Успешно', 'Успешно'), ('Не успешно', 'Не успешно')], max_length=20, verbose_name='Статус')),
                ('server_response', models.TextField(blank=True, verbose_name='Ответ почтового сервера')),
                ('mailing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='mailing.mailing', verbose_name='Рассылка')),
                ('recipient', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mailing_attempts', to='mailing.recipient', verbose_name='Получатель')),
            ],
            options={
                'verbose_name': 'попытка рассылки',
                'verbose_name_plural': 'попытки рассылок',
                'ordering': ['-attempt_time'],
            },
        ),
        migrations.AlterModelOptions(
            name='recipient',
            options={'ordering': ['full_name', 'email'], 'permissions': [('view_all_recipients', 'Can view all recipients')], 'verbose_name': 'получатель рассылки', 'verbose_name_plural': 'получатели рассылки'},
        ),
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['subject'], 'verbose_name': 'сообщение', 'verbose_name_plural': 'сообщения'},
        ),
        migrations.AlterModelOptions(
            name='mailing',
            options={'ordering': ['-start_time'], 'permissions': [('disable_mailing', 'Can disable mailing'), ('view_all_mailings', 'Can view all mailings')], 'verbose_name': 'рассылка', 'verbose_name_plural': 'рассылки'},
        ),
    ]
