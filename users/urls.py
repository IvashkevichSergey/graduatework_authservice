from django.urls import path
from users.apps import UsersConfig
from users.views import LoginView, UsersListAPIView, \
    UserDetailAPIView, AuthView, LogoutView

app_name = UsersConfig.name


urlpatterns = [
    path('auth/', AuthView.as_view(), name='user_auth'),
    path('login/', LoginView.as_view(), name='user_login'),
    path('logout/', LogoutView.as_view(), name='user_logout'),
    path('profile/', UserDetailAPIView.as_view(), name='user_profile'),

    path('list/', UsersListAPIView.as_view(), name='user_list'),
    path('list/<int:pk>', UserDetailAPIView.as_view(), name='user_detail'),
]
