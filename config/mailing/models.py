from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class OwnedQuerySet(models.QuerySet):
    def visible_to(self, user):
        if user.is_superuser or user.groups.filter(name='Managers').exists():
            return self
        return self.filter(owner=user)


class Recipient(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=255, verbose_name='Ф. И. О.')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipients',
        null=True,
        blank=True,
        verbose_name='Владелец',
    )

    objects = OwnedQuerySet.as_manager()

    class Meta:
        verbose_name = 'получатель рассылки'
        verbose_name_plural = 'получатели рассылки'
        ordering = ['full_name', 'email']
        permissions = [
            ('view_all_recipients', 'Can view all recipients'),
        ]

    def __str__(self):
        return f'{self.full_name} ({self.email})'


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages',
        null=True,
        blank=True,
        verbose_name='Владелец',
    )

    objects = OwnedQuerySet.as_manager()

    class Meta:
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'
        ordering = ['subject']

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    CREATED = 'Создана'
    RUNNING = 'Запущена'
    COMPLETED = 'Завершена'

    STATUS_CHOICES = [
        (CREATED, 'Создана'),
        (RUNNING, 'Запущена'),
        (COMPLETED, 'Завершена'),
    ]

    start_time = models.DateTimeField(verbose_name='Дата и время начала отправки')
    end_time = models.DateTimeField(verbose_name='Дата и время окончания отправки')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=CREATED,
        verbose_name='Статус',
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='Сообщение',
    )
    recipients = models.ManyToManyField(
        Recipient,
        related_name='mailings',
        verbose_name='Получатели',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mailings',
        null=True,
        blank=True,
        verbose_name='Владелец',
    )
    is_enabled = models.BooleanField(default=True, verbose_name='Включена')

    objects = OwnedQuerySet.as_manager()

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'
        ordering = ['-start_time']
        permissions = [
            ('disable_mailing', 'Can disable mailing'),
            ('view_all_mailings', 'Can view all mailings'),
        ]

    @classmethod
    def calculate_status(cls, start_time, end_time):
        now = timezone.now()
        if now < start_time:
            return cls.CREATED
        if start_time <= now <= end_time:
            return cls.RUNNING
        return cls.COMPLETED

    def refresh_status(self, save=True):
        new_status = self.calculate_status(self.start_time, self.end_time)
        if self.status != new_status:
            self.status = new_status
            if save and self.pk:
                self.save(update_fields=['status'])
        return self.status

    def clean(self):
        super().clean()
        now = timezone.now()
        if self.start_time and self.pk is None and self.start_time < now:
            raise ValidationError({'start_time': 'Дата начала не может быть в прошлом.'})
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({'end_time': 'Дата начала должна быть раньше даты окончания.'})

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            self.status = self.calculate_status(self.start_time, self.end_time)
        super().save(*args, **kwargs)

    def can_send(self):
        return self.is_enabled and self.start_time <= timezone.now() <= self.end_time

    def __str__(self):
        return f'Рассылка №{self.pk}: {self.message}'


class MailingAttempt(models.Model):
    SUCCESS = 'Успешно'
    FAILURE = 'Не успешно'

    STATUS_CHOICES = [
        (SUCCESS, 'Успешно'),
        (FAILURE, 'Не успешно'),
    ]

    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='Статус')
    server_response = models.TextField(blank=True, verbose_name='Ответ почтового сервера')
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Рассылка',
    )
    recipient = models.ForeignKey(
        Recipient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mailing_attempts',
        verbose_name='Получатель',
    )

    class Meta:
        verbose_name = 'попытка рассылки'
        verbose_name_plural = 'попытки рассылок'
        ordering = ['-attempt_time']

    def __str__(self):
        recipient = self.recipient.email if self.recipient else 'получатель удален'
        return f'{self.mailing_id} — {recipient} — {self.status}'
