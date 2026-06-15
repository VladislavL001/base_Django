from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import MailingForm, MessageForm, RecipientForm
from .models import Mailing, MailingAttempt, Message, Recipient
from .services import send_mailing


def main_view(request):

    now = timezone.now()

    total_mailings = Mailing.objects.count()

    active_mailings = Mailing.objects.filter(
        start_time__lte=now, end_time__gte=now, status=Mailing.RUNNING
    ).count()

    total_recipients = Recipient.objects.count()

    successful_attempts = MailingAttempt.objects.filter(
        status=MailingAttempt.SUCCESS
    ).count()

    failed_attempts = MailingAttempt.objects.filter(
        status=MailingAttempt.FAILED
    ).count()

    sent_messages = successful_attempts

    stats = cache.get("main_page_stats")
    if not stats:
        stats = {
            "total_mailings": total_mailings,
            "active_mailings": active_mailings,
            "total_recipients": total_recipients,
            "successful_attempts": successful_attempts,
            "failed_attempts": failed_attempts,
            "sent_messages": sent_messages,
        }

        cache.set("main_page_stats", stats, 60 * 15)

    context = stats

    return render(request, "mailing/main.html", context)


def is_manager(user):
    return user.groups.filter(name="Менеджер").exists()


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
        mailing = get_object_or_404(Mailing, pk=pk)

        try:
            send_mailing(mailing.pk)

            messages.success(request, "Рассылка успешно отправлена")

        except ValueError as e:
            messages.error(request, str(e))

        return redirect("mailing:mailing_detail", pk=mailing.pk)


class MailingToggleActiveView(LoginRequiredMixin, View):

    def get(self, request, pk):

        if not is_manager(request.user):
            return redirect("mailing:main")

        mailing = get_object_or_404(Mailing, pk=pk)

        mailing.is_active = not mailing.is_active

        mailing.save(update_fields=["is_active"])

        return redirect("mailing:mailing_list")



class RecipientListView(BaseListView):
    model = Recipient
    context_object_name = "recipients"

    def get_queryset(self):
        if is_manager(self.request.user):
            return Recipient.objects.all()

        return Recipient.objects.filter(owner=self.request.user)


class RecipientDetailView(BaseDetailView):
    model = Recipient
    context_object_name = "recipient"

    def get_queryset(self):
        if is_manager(self.request.user):
            return Recipient.objects.all()

        return Recipient.objects.filter(owner=self.request.user)


class RecipientCreateView(BaseCreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/form.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(BaseUpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/form.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def get_queryset(self):
        return Recipient.objects.filter(owner=self.request.user)


class RecipientDeleteView(BaseDeleteView):
    model = Recipient
    template_name = "mailing/confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def get_queryset(self):
        return Recipient.objects.filter(owner=self.request.user)


class MessageListView(BaseListView):
    model = Message
    context_object_name = "messages"

    def get_queryset(self):
        if is_manager(self.request.user):
            return Message.objects.all()

        return Message.objects.filter(
            owner=self.request.user
        )


class MessageDetailView(BaseDetailView):
    model = Message
    context_object_name = "message"

    def get_queryset(self):
        if is_manager(self.request.user):
            return Message.objects.all()

        return Message.objects.filter(
            owner=self.request.user
        )


class MessageCreateView(BaseCreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/form.html"
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(BaseUpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/form.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_queryset(self):
        return Message.objects.filter(
            owner=self.request.user
        )


class MessageDeleteView(BaseDeleteView):
    model = Message
    template_name = "mailing/confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_queryset(self):
        return Message.objects.filter(
            owner=self.request.user
        )



class MailingListView(BaseListView):
    model = Mailing
    context_object_name = "mailing"

    def get_queryset(self):
        if is_manager(self.request.user):
            return Mailing.objects.all()

        return Mailing.objects.filter(owner=self.request.user)


class MailingDetailView(BaseDetailView):
    model = Mailing
    context_object_name = "mailing"

    def get_queryset(self):
        if is_manager(self.request.user):
            return Mailing.objects.all()

        return Mailing.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(BaseCreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(BaseUpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingDeleteView(BaseDeleteView):
    model = Mailing
    template_name = "mailing/confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)
