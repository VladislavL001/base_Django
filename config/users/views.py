from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserRegisterForm
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView

User = get_user_model()


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def dispatch(self, request, *args, **kwargs):

        if not request.user.groups.filter(
            name='Менеджер'
        ).exists():
            return redirect('mailing:main')

        return super().dispatch(
            request,
            *args,
            **kwargs
        )