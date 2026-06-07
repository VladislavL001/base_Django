from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import MailingForm, MessageForm, RecipientForm
from .models import Mailing, MailingAttempt, Message, Recipient
from .services import MailingUnavailableError, send_mailing


def is_manager(user):
    return user.is_superuser or user.groups.filter(name='Managers').exists()


class MainView(TemplateView):
    template_name = 'mailing/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        stats = cache.get('main_stats')
        if stats is None:
            Mailing.objects.filter(start_time__gt=now).exclude(status=Mailing.CREATED).update(status=Mailing.CREATED)
            Mailing.objects.filter(start_time__lte=now, end_time__gte=now).exclude(status=Mailing.RUNNING).update(status=Mailing.RUNNING)
            Mailing.objects.filter(end_time__lt=now).exclude(status=Mailing.COMPLETED).update(status=Mailing.COMPLETED)
            stats = {
                'mailings_count': Mailing.objects.count(),
                'active_mailings_count': Mailing.objects.filter(
                    start_time__lte=now,
                    end_time__gte=now,
                    status=Mailing.RUNNING,
                    is_enabled=True,
                ).count(),
                'recipients_count': Recipient.objects.count(),
            }
            cache.set('main_stats', stats, 60)
        context.update(stats)
        return context


def main_view(request):
    response = MainView.as_view()(request)
    response['Cache-Control'] = 'public, max-age=60'
    return response


class OwnershipQuerySetMixin(LoginRequiredMixin):
    model = None

    def get_queryset(self):
        queryset = super().get_queryset()
        if is_manager(self.request.user):
            return queryset
        return queryset.filter(owner=self.request.user)


class OwnerAssignMixin(LoginRequiredMixin):
    def form_valid(self, form):
        if not form.instance.owner_id:
            form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerEditMixin(OwnershipQuerySetMixin, UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.owner_id == self.request.user.id or self.request.user.is_superuser


class RecipientListView(OwnershipQuerySetMixin, ListView):
    model = Recipient
    context_object_name = 'recipients'


class RecipientDetailView(OwnershipQuerySetMixin, DetailView):
    model = Recipient
    context_object_name = 'recipient'


class RecipientCreateView(OwnerAssignMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:recipient_list')


class RecipientUpdateView(OwnerEditMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:recipient_list')


class RecipientDeleteView(OwnerEditMixin, DeleteView):
    model = Recipient
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:recipient_list')


class MessageListView(OwnershipQuerySetMixin, ListView):
    model = Message
    context_object_name = 'messages'


class MessageDetailView(OwnershipQuerySetMixin, DetailView):
    model = Message
    context_object_name = 'message'


class MessageCreateView(OwnerAssignMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:message_list')


class MessageUpdateView(OwnerEditMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:message_list')


class MessageDeleteView(OwnerEditMixin, DeleteView):
    model = Message
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')


class MailingListView(OwnershipQuerySetMixin, ListView):
    model = Mailing
    context_object_name = 'mailings'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('message', 'owner').prefetch_related('recipients')
        for mailing in queryset:
            mailing.refresh_status()
        return queryset


class MailingDetailView(OwnershipQuerySetMixin, DetailView):
    model = Mailing
    context_object_name = 'mailing'

    def get_queryset(self):
        return super().get_queryset().select_related('message', 'owner').prefetch_related('recipients', 'attempts')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.refresh_status()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attempts'] = self.object.attempts.select_related('recipient')[:20]
        return context


class MailingCreateView(OwnerAssignMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class MailingUpdateView(OwnerEditMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class MailingDeleteView(OwnerEditMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'mailing/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailings = Mailing.objects.all() if is_manager(self.request.user) else Mailing.objects.filter(owner=self.request.user)
        attempts = MailingAttempt.objects.filter(mailing__in=mailings)
        context['mailings_count'] = mailings.count()
        context['success_attempts'] = attempts.filter(status=MailingAttempt.SUCCESS).count()
        context['failed_attempts'] = attempts.filter(status=MailingAttempt.FAILURE).count()
        context['sent_messages'] = context['success_attempts']
        context['mailing_stats'] = mailings.annotate(
            success_count=Count('attempts', filter=Q(attempts__status=MailingAttempt.SUCCESS)),
            failure_count=Count('attempts', filter=Q(attempts__status=MailingAttempt.FAILURE)),
        )
        return context


@login_required
@require_POST
def launch_mailing_view(request, pk):
    queryset = Mailing.objects.all() if request.user.is_superuser else Mailing.objects.filter(owner=request.user)
    mailing = get_object_or_404(queryset, pk=pk)
    try:
        result = send_mailing(mailing)
        messages.success(
            request,
            f"Рассылка выполнена: успешно — {result['success']}, не успешно — {result['failure']}.",
        )
    except MailingUnavailableError as exc:
        messages.error(request, str(exc))
    return redirect('mailing:mailing_detail', pk=mailing.pk)


@login_required
@require_POST
def disable_mailing_view(request, pk):
    if not is_manager(request.user):
        messages.error(request, 'Отключать рассылки может только менеджер.')
        return redirect('mailing:mailing_detail', pk=pk)
    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.is_enabled = False
    mailing.save(update_fields=['is_enabled'])
    messages.success(request, 'Рассылка отключена.')
    return redirect('mailing:mailing_detail', pk=mailing.pk)
