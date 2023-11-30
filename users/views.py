from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from rest_framework import generics, status
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.serializers import UserListSerializer, UserAuthSerializer, UserDetailSerializer
from users.services import generate_auth_code


@csrf_exempt
@require_POST
def auth_user(request: Request) -> JsonResponse:
    """Контроллер получает введённый пользователем номер телефона,
    проверяет его через сериализатор и при успешной валидации
    перенаправляет пользователя на страницу ввода кода авторизации,
    предварительно сохраняя номер телефона в текущую сессию"""
    data = JSONParser().parse(request)
    serializer = UserAuthSerializer(data=data)
    if serializer.is_valid():
        request.session['phone_number'] = serializer.data.get('phone_number')
        return redirect('users:user_login')
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Контроллер для проведения авторизации пользователя по
    сгенерированному коду авторизации"""

    def post(self, request: Request) -> Response:
        """Обработка POST запроса пользователя на авторизацию"""
        phone = request.session.get('phone_number')
        user_code = request.data.get('verification_code')
        verification_code = request.session.get('code')

        # Проверка на существование сохранённого в текущей сессии
        # номера телефона и кода авторизации
        if not phone or not verification_code:
            return Response(
                {'Ошибка': 'Данная сессия больше неактивна. '
                           'Повторно отправьте номер телефона '
                           'по адресу /users/auth/'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка на наличие заполненного пользователем
        # поля verification_code
        if not user_code:
            return Response(
                {'Ошибка': 'Поле verification_code '
                           'является обязательными для заполнения'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Передача данных в класс авторизации
        user = authenticate(request=request, phone_number=phone, verification_code=user_code)

        # Проверка на корректность введённого кода авторизации
        if user is None:
            return Response(
                {'Ошибка': 'Код введён некорректно, повторите попытку.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Сохранение авторизованного пользователя в сессии
        login(request, user)
        return Response(
            {'Ответ от сервера': 'Авторизация прошла успешно'},
            status=status.HTTP_200_OK
        )

    def get(self, request: Request) -> Response:
        """Обработка GET запроса для авторизации пользователя"""

        # Проверка на существование сохранённого в текущей сессии
        # номера телефона по ключу 'phone_number'
        if not request.session.get('phone_number'):
            return Response(
                {'Ошибка': 'Данная сессия больше неактивна. '
                           'Повторно отправьте номер телефона '
                           'по адресу /users/auth/'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Генерируем код и сохраняем его в текущей сессии
        code = generate_auth_code()
        request.session['code'] = code
        print('Код верификации', request.session.get('code'))

        return Response(
            {'Ответ от сервера': 'Введите код верификации в поле \'verification_code\''
                                 ' по адресу /users/login/'},
            status=status.HTTP_200_OK
        )


class UsersListAPIView(generics.ListAPIView):
    """Контроллер для отображения списка пользователей"""
    queryset = User.objects.all()
    serializer_class = UserListSerializer


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Контроллер для отображения детальной информации о пользователях"""
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer


@csrf_exempt
@require_GET
def logout_view(request: Request) -> JsonResponse:
    """Контроллер для удаления пользователя из текущей сессии"""
    if not request.user.is_authenticated:
        return JsonResponse(
            {'Ответ от сервера': 'Вы не авторизованы в системе'},
            status=status.HTTP_400_BAD_REQUEST
        )

    logout(request)
    return JsonResponse(
        {'Ответ от сервера': 'Вы успешно вышли из системы'},
        status=status.HTTP_200_OK
    )


@csrf_exempt
@require_GET
def profile(request: Request) -> JsonResponse:
    """Контроллер для проверки статуса авторизоции пользователя"""
    if not request.user.is_authenticated:
        return JsonResponse({'Текущий статус': 'Вы не авторизованы в системе'})
    serializer = UserDetailSerializer(request.user)
    return JsonResponse(serializer.data)
