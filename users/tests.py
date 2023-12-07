from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotAuthenticated
from rest_framework.test import APITestCase, APIClient

from users.models import User


class UsersAuthTestCase(APITestCase):
    """Класс для тестирования эндпоинтов сервиса авторизации"""

    def setUp(self):
        """Функция создаёт набор объектов перед каждым тестированием"""

        self.client = APIClient()
        self.data = {"phone_number": "89500626262"}

    def test_get_login(self):
        """Тест GET запроса по эндпоинту /users/login/"""

        response = self.client.get(reverse('users:user_login'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_login(self):
        """Тест POST запроса на отправку номера телефона
        по эндпоинту /users/login/"""

        response = self.client.post(
            reverse('users:user_login'), data=self.data
        )
        self.assertRedirects(response, '/users/auth/')
        self.assertTrue(self.client.session.get('phone_number'))
        self.assertTrue(self.client.session.get('code'))

    def test_post_blank_login(self):
        """Тест POST запроса на валидацию (отправка пустой формы)
        по эндпоинту /users/login/"""

        self.data = {"": ""}
        response = self.client.post(reverse('users:user_login'), data=self.data)
        self.assertRaises(ValidationError)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_wrong_login(self):
        """Тест POST запроса на валидацию (отправка некорректной формы)
        по эндпоинту /users/login/"""

        self.data = {"phone_number": "123"}
        response = self.client.post(reverse('users:user_login'), data=self.data)
        self.assertRaises(ValidationError)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_auth_wrong_session(self):
        """Тест GET запроса по эндпоинту /users/auth/ с устаревшей сессией"""

        response = self.client.get(reverse('users:user_auth'))
        self.assertEqual(
            response.json(),
            {'Ошибка': 'Данная сессия больше неактивна. '
                       'Повторно отправьте номер телефона '
                       'по адресу /users/auth/'})

    def test_post_auth(self):
        """Тест POST запроса на отправку кода верификации
        по эндпоинту /users/auth/"""

        self.client.post(reverse('users:user_login'), data=self.data)
        self.client.get(reverse('users:user_auth'))

        self.data = {"verification_code": self.client.session.get('code')}
        response = self.client.post(reverse('users:user_auth'), data=self.data)
        self.assertEqual(
            response.json(),
            {'Ответ от сервера': 'Авторизация прошла успешно'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.all().count(), 1)

    def test_post_wrong_auth(self):
        """Тест POST запроса на валидацию кода верификации
        по эндпоинту /users/auth/"""

        self.client.post(reverse('users:user_login'), data=self.data)
        self.client.get(reverse('users:user_auth'))

        self.data = {"verification_code": "9999"}
        response = self.client.post(reverse('users:user_auth'), data=self.data)
        self.assertEqual(
            response.json(),
            {'Ошибка авторизации': 'Код введён некорректно, повторите попытку'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_profile(self):
        """Тест GET запроса по эндпоинту /users/profile/ """

        response = self.client.get(reverse('users:user_profile'))
        self.assertEqual(
            response.json(),
            {'detail': 'Учетные данные не были предоставлены.'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_logout(self):
        """Тест GET запроса по эндпоинту /users/logout/ """

        response = self.client.get(reverse('users:user_logout'))
        self.assertRaises(NotAuthenticated)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
