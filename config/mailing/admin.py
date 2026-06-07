from django.contrib import admin

from .models import Mailing, MailingAttempt, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'owner')
    search_fields = ('email', 'full_name')
    list_filter = ('owner',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'owner')
    search_fields = ('subject', 'body')
    list_filter = ('owner',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'start_time', 'end_time', 'status', 'is_enabled', 'owner')
    list_filter = ('status', 'is_enabled', 'owner')
    search_fields = ('message__subject',)
    filter_horizontal = ('recipients',)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('attempt_time', 'mailing', 'recipient', 'status')
    list_filter = ('status', 'attempt_time')
    search_fields = ('server_response', 'recipient__email')
