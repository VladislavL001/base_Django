from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Message, Recipient, Mailing


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = '__all__'

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = '__all__'

class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and start_time < timezone.now():
            raise forms.ValidationError(
                'Дата начала не может быть в прошлом.'
            )

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError(
                'Дата начала должна быть раньше даты окончания.'
            )

        return cleaned_data