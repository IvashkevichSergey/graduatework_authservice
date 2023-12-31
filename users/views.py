from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from rest_framework import generics, status, exceptions
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.views import APIView
from rest_framework.authentication import authenticate
from users.models import User
from users.serializers import UserLoginSerializer, UserSerializer, CodeAuthSerializer
from users.services import generate_auth_code, check_user_auth


def main_page_view(request) -> HttpResponseRedirect:
    return HttpResponseRedirect(
        reverse_lazy('users:user_login', request=request)
    )


class LoginView(GenericAPIView):
    """Контроллер получает введённый пользователем номер телефона,
    и при успешной валидации номера перенаправляет пользователя
    на страницу ввода кода авторизации, предварительно сохраняя номер
    телефона в текущую сессию"""
    serializer_class = UserLoginSerializer

    def get(self, request: Request) -> Response:
        """Страница с инструкцией об отправке номера телефона"""

        # Проверяем авторизован ли пользователь
        check_user_auth(request)

        return Response({
            "Ответ от сервера": "Необходимо отправить номер телефона "
                                "POST запросом по форме "
                                "\"phone_number\": 8XXXXXXXXXX"},
            status=status.HTTP_200_OK
        )

    def post(self, request: Request) -> (Response, HttpResponseRedirect):
        """Обработка POST запроса пользователя на авторизацию.
        Задаётся длительность хранения номера телефона в сессии - 5 минут
        """

        # Проверяем авторизован ли пользователь
        check_user_auth(request)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.session['phone_number'] = serializer.data.get('phone_number')
        request.session.set_expiry(300)
        return HttpResponseRedirect(reverse_lazy('users:user_auth'))


class AuthView(GenericAPIView):
    """Контроллер для проведения авторизации пользователя по
    сгенерированному коду авторизации"""
    serializer_class = CodeAuthSerializer

    def get(self, request: Request) -> (Response, HttpResponseRedirect):
        """Обработка GET запроса для авторизации пользователя"""

        # Проверяем авторизован ли пользователь
        check_user_auth(request)

        # Проверка на существование сохранённого в текущей сессии
        # номера телефона по ключу 'phone_number'
        if not request.session.get('phone_number'):
            raise exceptions.PermissionDenied(
                {'Ошибка': 'Данная сессия больше неактивна. '
                           'Повторно отправьте номер телефона '
                           'по адресу /users/auth/'}
            )

        # Генерируем код и сохраняем его в текущей сессии
        code = generate_auth_code()
        request.session['code'] = code
        print('Код авторизации', request.session.get('code'))

        return Response(
            {'Ответ от сервера': f'Введите код авторизации ({code}) в поле '
                                 f'\'verification_code\' по адресу /users/auth'},
            status=status.HTTP_200_OK
        )

    def post(self, request: Request) -> (HttpResponseRedirect, Response):
        """Обработка POST запроса пользователя на авторизацию"""

        # Проверяем авторизован ли пользователь
        check_user_auth(request)

        user_phone = request.session.get('phone_number')
        verification_code = request.session.get('code')

        # Проверяем что с момента отправки номера телефона
        # сессия всё ещё активна
        if not user_phone or not verification_code:
            raise exceptions.PermissionDenied(
                {'Ошибка': 'Данная сессия больше неактивна. '
                           'Повторно отправьте номер телефона '
                           'по адресу /users/login'}
            )

        user = authenticate(
            request=request,
            phone_number=user_phone,
            verification_code=verification_code,
        )

        # Сохранение авторизованного пользователя в сессии
        login(request, user)

        return HttpResponseRedirect(reverse_lazy('users:user_profile'))


class UsersListAPIView(generics.ListAPIView):
    """Контроллер для отображения списка пользователей"""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailAPIView(generics.RetrieveUpdateAPIView):
    """Контроллер для отображения детальной информации о пользователе"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user


class LogoutView(APIView):
    """Контроллер для удаления пользователя из текущей сессии"""

    def get(self, request: Request) -> Response:
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated(
                {'Ошибка доступа': 'Вы не авторизованы в системе'}
            )

        logout(request)
        return Response(
            {'Ответ от сервера': 'Вы успешно вышли из системы'},
            status=status.HTTP_200_OK
        )
