from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from rest_framework import generics, status, viewsets, authentication, exceptions
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.serializers import UserSerializer, UserListSerializer, UserAuthSerializer, UserDetailSerializer
from users.services import generate_auth_code


@csrf_exempt
@require_POST
def auth_user(request):
    data = JSONParser().parse(request)
    serializer = UserAuthSerializer(data=data)
    if serializer.is_valid():
        request.session['phone_number'] = serializer.data.get('phone_number')
        return redirect('users:user_login')
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        phone = request.session.get('phone_number')
        user_code = request.data.get('verification_code')
        verification_code = request.session.get('code')

        print(f'Номер телефона: {phone}. Код верификации: {verification_code}')

        if not phone or not verification_code:
            return Response(
                {'Ошибка': 'Данная сессия больше неактивна. '
                           'Повторно отправьте номер телефона '
                           'по адресу /users/auth/'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not user_code:
            return Response(
                {'Ошибка': 'Поле verification_code '
                           'является обязательными для заполнения'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request=request, phone_number=phone, verification_code=user_code)
        print(user)

        if user is None:
            return Response(
                {'Ошибка': 'Код введён некорректно, повторите попытку.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        login(request, user)
        return Response(
            {'Ответ от сервера': 'Авторизация прошла успешно'},
            status=status.HTTP_200_OK
        )

    def get(self, request):
        code = generate_auth_code()
        request.session['code'] = code
        print('Код верификации', request.session.get('code'))
        return Response(
            {'Ответ от сервера': 'Введите код верификации в поле \'verification_code\''
                                 ' по адресу /users/login/'},
            status=status.HTTP_200_OK
        )


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def perform_create(self, serializer):
        serializer.save().set_invite_code()


class UsersListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer


def whoami_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'Текущий статус': 'Вы не авторизованы в системе'})

    return JsonResponse({'Текущий пользователь': str(request.user)})


def logout_view(request):
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
