from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites import requests
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import MessageForm, RecipientForm, MailingForm
from .models import Message, Recipient, Mailing

def main_view(request):
    return render(request, 'mailing/main.html')

class BaseListView(LoginRequiredMixin, ListView):
    pass

class BaseDetailView(LoginRequiredMixin, DetailView):
    pass

class BaseCreateView(LoginRequiredMixin, CreateView):
    pass

class BaseUpdateView(LoginRequiredMixin, UpdateView):
    pass

class BaseDeleteView(LoginRequiredMixin, DeleteView):
    pass


class RecipientListView(BaseListView):
    model = Recipient
    context_object_name = 'recipients'


class RecipientDetailView(BaseDetailView):
    model = Recipient
    context_object_name = 'recipient'


class RecipientCreateView(BaseCreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:recipient_list')


class RecipientUpdateView(BaseUpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:recipient_list')


class RecipientDeleteView(BaseDeleteView):
    model = Recipient
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:recipient_list')


class MessageListView(BaseListView):
    model = Message
    context_object_name = 'messages'


class MessageDetailView(BaseDetailView):
    model = Message
    context_object_name = 'message'


class MessageCreateView(BaseCreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:message_list')


class MessageUpdateView(BaseUpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:message_list')


class MessageDeleteView(BaseDeleteView):
    model = Message
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')


class MailingListView(BaseListView):
    model = Mailing
    context_object_name = 'mailing'


class MailingDetailView(BaseDetailView):
    model = Mailing
    context_object_name = 'mailing'


class MailingCreateView(BaseCreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:mailing_list')


class MailingUpdateView(BaseUpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:mailing_list')


class MailingDeleteView(BaseDeleteView):
    model = Mailing
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')