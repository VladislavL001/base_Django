from django.utils import timezone

from django.db import models
from django.forms.fields import DateTimeField


class Recipient(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)

    def __str__(self):
        return self.full_name


class Message(models.Model):
    subject=models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.subject

class Mailing(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    CREATED = 'Created'
    RUNNING = 'Running'
    COMPLETED = 'Completed'

    status_list = [
        (COMPLETED, 'Завершена'),
        (CREATED, 'Создана'),
        (RUNNING, 'Запущена')
    ]
    status = models.CharField(
        max_length=20,
        choices = status_list,
        verbose_name= 'Статус'
    )

    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Recipient)


    def update_status(self):
        time_now = timezone.now()
        if time_now < self.start_time:
            new_status = self.CREATED
        elif self.start_time <= time_now <= self.end_time:
            new_status = self.RUNNING
        else:
            new_status = self.COMPLETED

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])

    def can_send(self):
        time_now = timezone.now()
        return self.start_time <= time_now <= self.end_time


    def __str__(self):
        return f'Рассылка {self.id} - {self.message}'


class MailingAttempt(models.Model):
    SUCCESS = 'Success'
    FAILED = 'Failed'

    STATUS_CHOICES = [
        (SUCCESS, 'Успешно'),
        (FAILED, 'Не успешно'),
    ]

    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='attempts'
    )

    attempt_time = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    server_response = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.mailing} - {self.status}'