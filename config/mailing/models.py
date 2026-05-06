import datetime

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
    date_first = models.DateTimeField()
    date_last = models.DateTimeField()

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

    def __str__(self):
        return f'Рассылка {self.id} - {self.message}'
