from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView

from .forms import UserRegisterForm
from .models import User
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse

User = get_user_model()


class UserToggleActiveView(LoginRequiredMixin, View):

    def get(self, request, pk):

        if not request.user.groups.filter(name="Менеджер").exists():

            return redirect("mailing:main")

        user = get_object_or_404(User, pk=pk)

        user.is_active = not user.is_active

        user.save(update_fields=["is_active"])

        return redirect("users:user_list")


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):

        user = form.save(commit=False)

        user.is_active = False

        user.save()

        token = default_token_generator.make_token(user)

        uid = urlsafe_base64_encode(
            force_bytes(user.pk)
        )

        verify_url = self.request.build_absolute_uri(
            reverse(
                "users:verify_email",
                kwargs={
                    "uidb64": uid,
                    "token": token,
                },
            )
        )

        send_mail(
            subject="Подтверждение регистрации",
            message=f"Перейдите по ссылке:\n{verify_url}",
            from_email=None,
            recipient_list=[user.email],
        )

        return redirect("users:login")


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"

    def dispatch(self, request, *args, **kwargs):

        if not request.user.groups.filter(name="Менеджер").exists():
            return redirect("mailing:main")

        return super().dispatch(request, *args, **kwargs)


class VerifyEmailView(View):

    def get(self, request, uidb64, token):

        try:
            uid = force_str(
                urlsafe_base64_decode(uidb64)
            )

            user = User.objects.get(pk=uid)

        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
        ):
            user = None

        if (
            user
            and default_token_generator.check_token(
                user,
                token,
            )
        ):
            user.is_active = True
            user.is_verified = True

            user.save(
                update_fields=[
                    "is_active",
                    "is_verified",
                ]
            )

            return redirect("users:login")

        return redirect("mailing:main")