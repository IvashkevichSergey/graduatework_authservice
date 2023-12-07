from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, CSRFCheck

from users.models import User
from users.services import check_verification_code


class CustomAuthBackend(BaseAuthentication):
    """
    Класс, отвечающий за авторизацию пользователей по
    номеру телефона и коду авторизации
    """

    def authenticate(self, request, phone_number=None, verification_code=None):

        # Валидация кода авторизации, введённого пользователем
        check_verification_code(
            request=request,
            verification_code=verification_code
        )

        # При авторизации ищем пользователя в БД. Если пользователь
        # не найден - записываем данные о новом пользователе в БД
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            user = User(phone_number=phone_number)
            user.set_invite_code()
            user.save()

        # Время жизни сессии будет определяться настройками
        # браузера пользователя
        request.session.set_expiry(None)

        # Если учётная запись пользователя не активна - доступ запрещаем
        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                {'Ошибка авторизации': 'Ваша учётная запись не активна. '
                                       'Свяжитесь с администратором'}
            )

        return user

    @staticmethod
    def get_user(user_id):
        return User.objects.get(pk=user_id)
