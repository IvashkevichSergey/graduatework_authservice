from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.serializers import UserListSerializer, UserAuthSerializer, UserDetailSerializer
from users.services import generate_auth_code


class AuthView(APIView):
    """Контроллер получает введённый пользователем номер телефона,
    и при успешной валидации номера перенаправляет пользователя
    на страницу ввода кода авторизации,
    предварительно сохраняя номер телефона в текущую сессию"""

    def get(self, request: Request) -> Response:
        return Response({
            "Ответ от сервера": "Необходимо отправить номер телефона "
                                "POST запросом по форме "
                                "\"phone_number\": 12345678910"},
            status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """Обработка POST запроса пользователя на авторизацию"""
        params = request.data
        serializer = UserAuthSerializer(data=params)
        if serializer.is_valid():
            request.session['phone_number'] = serializer.data.get('phone_number')
            return redirect('users:user_login')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Контроллер для проведения авторизации пользователя по
    сгенерированному коду авторизации"""

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

    def post(self, request: Request) -> Response:
        """Обработка POST запроса пользователя на авторизацию"""
        phone = request.session.get('phone_number')
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

        if not request.data:
            return Response(
                {'Ошибка': 'Введите код верификации в поле \'verification_code\''
                           ' по адресу /users/login/'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_code = request.data.get('verification_code')
        # Проверка на наличие заполненного пользователем
        # поля verification_code
        if not user_code:
            return Response(
                {'Ошибка': 'Поле \'verification_code\' '
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


class UsersListAPIView(generics.ListAPIView):
    """Контроллер для отображения списка пользователей"""
    queryset = User.objects.all()
    serializer_class = UserListSerializer


class UserDetailAPIView(generics.RetrieveUpdateAPIView):
    """Контроллер для отображения детальной информации о пользователе"""
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    def get_object(self) -> User:
        return self.request.user

    def get(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        if not request.user.is_authenticated:
            return Response(
                {'Текущий статус': 'Вы не авторизованы в системе'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().get(request, *args, **kwargs)


class LogoutView(APIView):
    """Контроллер для удаления пользователя из текущей сессии"""

    def get(self, request: Request) -> Response:
        if not request.user.is_authenticated:
            return Response(
                {'Ответ от сервера': 'Вы не авторизованы в системе'},
                status=status.HTTP_400_BAD_REQUEST
            )

        logout(request)
        return Response(
            {'Ответ от сервера': 'Вы успешно вышли из системы'},
            status=status.HTTP_200_OK
        )
