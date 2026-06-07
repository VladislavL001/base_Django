from django.urls import path

from .views import UserListView, activate_view, block_user_view, register_view

app_name = 'users'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('activate/<uidb64>/<token>/', activate_view, name='activate'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/block/', block_user_view, name='block_user'),
]
