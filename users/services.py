import random
from time import sleep

from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse

from users.models import User


def generate_auth_code():
    # sleep(2)
    code = random.randint(1000, 9999)
    return code


class SettingsBackend(BaseBackend):
    """
    Класс, отвечающий за аутентификацию пользователей по
    номеру телефона и коду авторизации
    """

    def authenticate(self, request, phone_number=None, verification_code=None):
        code = request.session.get('code')
        if phone_number and verification_code and verification_code == code:
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                user = User(phone_number=phone_number)
                user.set_invite_code()
                user.save()
            return user
        return None

    def get_user(self, user_id):
        return User.objects.get(pk=user_id)
