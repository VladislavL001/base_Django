from django.contrib import admin
from .models import Recipient, Message, Mailing

admin.site.register(Recipient)
admin.site.register(Message)
admin.site.register(Mailing)