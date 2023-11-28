from django.urls import path
from rest_framework.authentication import BaseAuthentication

from users.apps import UsersConfig
from users.views import UserCreateAPIView, LoginView, UsersListAPIView, \
    whoami_view, logout_view, auth_user, UserDetailAPIView

app_name = UsersConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(), name='user_login'),
    path('logout/', logout_view, name='user_logout'),
    path('whoami/', whoami_view, name='user_whoami'),
    path('auth/', auth_user, name='user_auth'),
    path('register/', UserCreateAPIView.as_view(), name='user_create'),

    path('list/', UsersListAPIView.as_view(), name='user_list'),
    path('list/<int:pk>', UserDetailAPIView.as_view(), name='user_detail'),
]