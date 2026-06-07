from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from .forms import RegisterForm


def is_manager(user):
    return user.is_superuser or user.groups.filter(name='Managers').exists()


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            path = reverse('users:activate', kwargs={'uidb64': uid, 'token': token})
            activation_url = f'http://{get_current_site(request).domain}{path}'
            send_mail(
                'Подтверждение регистрации',
                f'Для активации аккаунта перейдите по ссылке: {activation_url}',
                None,
                [user.email],
                fail_silently=False,
            )
            messages.success(request, 'Проверьте email и подтвердите регистрацию.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=['is_active'])
        messages.success(request, 'Email подтвержден. Теперь можно войти.')
    else:
        messages.error(request, 'Ссылка активации недействительна.')
    return redirect('login')


class ManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_manager(self.request.user)


class UserListView(ManagerRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'service_users'
    ordering = ['username']


@login_required
@require_POST
def block_user_view(request, pk):
    if not is_manager(request.user):
        messages.error(request, 'Блокировать пользователей может только менеджер.')
        return redirect('mailing:main')
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'Нельзя заблокировать самого себя.')
    else:
        user.is_active = False
        user.save(update_fields=['is_active'])
        messages.success(request, f'Пользователь {user.username} заблокирован.')
    return redirect('users:user_list')
