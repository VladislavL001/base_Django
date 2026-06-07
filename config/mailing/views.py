from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import MessageForm, RecipientForm, MailingForm
from .models import Message, Recipient, Mailing
from .services import send_mailing
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from django.contrib.auth.models import Group


def main_view(request):

    now = timezone.now()

    total_mailings = Mailing.objects.count()

    active_mailings = Mailing.objects.filter(
        start_time__lte=now,
        end_time__gte=now,
        status=Mailing.RUNNING
    ).count()

    total_recipients = Recipient.objects.count()

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'total_recipients': total_recipients,
    }

    return render(
        request,
        'mailing/main.html',
        context
    )

def is_manager(user):
    return user.groups.filter(name='Менеджер').exists()

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

from django.views import View

class MailingSendView(LoginRequiredMixin, View):

    def get(self, request, pk):
        mailing = get_object_or_404(
            Mailing,
            pk=pk
        )

        try:
            send_mailing(mailing.pk)

            messages.success(
                request,
                'Рассылка успешно отправлена'
            )

        except ValueError as e:
            messages.error(
                request,
                str(e)
            )

        return redirect(
            'mailing:mailing_detail',
            pk=mailing.pk
        )


class RecipientListView(BaseListView):
    model = Recipient
    context_object_name = 'recipients'

    def get_queryset(self):
        if is_manager(self.request.user):
            return Recipient.objects.all()

        return Recipient.objects.filter(
            owner=self.request.user
        )

class RecipientDetailView(BaseDetailView):
    model = Recipient
    context_object_name = 'recipient'

    def get_queryset(self):
        if is_manager(self.request.user):
            return Recipient.objects.all()

        return Recipient.objects.filter(
            owner=self.request.user
        )


class RecipientCreateView(BaseCreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(BaseUpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def get_queryset(self):
        return Recipient.objects.filter(
            owner=self.request.user
        )


class RecipientDeleteView(BaseDeleteView):
    model = Recipient
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def get_queryset(self):
        return Recipient.objects.filter(
            owner=self.request.user
        )


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

    def get_queryset(self):
        if is_manager(self.request.user):
            return Mailing.objects.all()

        return Mailing.objects.filter(
            owner=self.request.user
        )


class MailingDetailView(BaseDetailView):
    model = Mailing
    context_object_name = 'mailing'

    def get_queryset(self):
        if is_manager(self.request.user):
            return Mailing.objects.all()

        return Mailing.objects.filter(
            owner=self.request.user
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(BaseCreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(BaseUpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        return Mailing.objects.filter(
            owner=self.request.user
        )


class MailingDeleteView(BaseDeleteView):
    model = Mailing
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        return Mailing.objects.filter(
            owner=self.request.user
        )