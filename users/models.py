import random
import string
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя сервисом"""
    username = None
    phone_number = models.PositiveBigIntegerField(unique=True)
    invite_code = models.CharField(max_length=6)
    invited_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)

    def set_invite_code(self):
        """Генерируем инвайт-код при первой авторизации пользователя"""
        chars = string.ascii_letters + string.digits
        password = ''.join(random.sample(chars, 6))
        self.invite_code = password
        self.save()

    def __str__(self):
        """Строковое представление модели пользователя"""
        return f'Пользователь "{self.pk}" с номером {self.phone_number}'

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
