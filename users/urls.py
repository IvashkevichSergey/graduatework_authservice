from django.urls import path
from users.apps import UsersConfig
from users.views import LoginView, UsersListAPIView, \
    logout_view, auth_user, UserDetailAPIView, profile

app_name = UsersConfig.name

urlpatterns = [
    path('auth/', auth_user, name='user_auth'),
    path('login/', LoginView.as_view(), name='user_login'),
    path('logout/', logout_view, name='user_logout'),
    path('profile/', profile, name='user_profile'),

    path('list/', UsersListAPIView.as_view(), name='user_list'),
    path('list/<int:pk>', UserDetailAPIView.as_view(), name='user_detail'),
]
