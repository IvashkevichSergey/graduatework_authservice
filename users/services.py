import random
from time import sleep

from django.contrib.auth.backends import BaseBackend
from users.models import User


def generate_auth_code() -> int:
    """Функция для генерации случайного 4-х значного кода
     при авторизации пользователя"""
    sleep(2)
    code = random.randint(1000, 9999)
    return code


class SettingsBackend(BaseBackend):
    """
    Класс, отвечающий за аутентификацию пользователей по
    номеру телефона и коду авторизации
    """

    def authenticate(self, request, phone_number=None, verification_code=None):
        # Получаем из сессии сгенерированный ранее код
        code = request.session.get('code')

        # Если данные переданы в функцию корректно, то ищем пользователя
        # в БД. Если пользователь не найден - записываем данные о новом
        # пользователе в БД
        if phone_number and verification_code and int(verification_code) == code:
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
