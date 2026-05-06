from django import forms

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