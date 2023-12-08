import random
from time import sleep
from rest_framework import status, exceptions
from rest_framework.request import Request
from users.serializers import CodeAuthSerializer


def generate_auth_code() -> int:
    """Функция для генерации случайного 4-х значного кода
     при авторизации пользователя"""
    sleep(2)
    code = random.randint(1000, 9999)
    return code


def check_verification_code(request: Request,
                            verification_code: str) -> None:
    """Функция проверяет отправляемые пользователем данные
    по эндпоинту /users/login/"""
    # Первичная валидация вводимых данных посредством сериализатора
    serializer = CodeAuthSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_code = serializer.data.get('verification_code')
    # Проверка вводимого пользователем кода и сгенерированного
    if user_code != verification_code:
        raise exceptions.ValidationError(
            {'Ошибка авторизации': 'Код введён некорректно, повторите попытку'}
        )


def check_user_auth(request: Request) -> None:
    """Функция проверяет авторизован ли пользователь перед отправкой
    GET/POST запросов по эндпоинтам /users/login/ и /users/auth/"""
    if not request.user.is_anonymous:
        raise exceptions.ValidationError(
            {'Ошибка доступа': f'Вы уже авторизованы как \"{request.user}\"'}
        )
