import random
import string
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя сервисом"""
    username = None
    password = None
    phone_number = models.PositiveBigIntegerField(
        unique=True, help_text='Номер телефона'
    )
    invite_code = models.CharField(
        max_length=6, null=True, unique=True,
        help_text='Инвайт-код пользователя'
    )
    invited_by = models.ForeignKey(
        to='self', to_field='invite_code',
        null=True, on_delete=models.SET_NULL,
        help_text='Инвайт-код пригласившего пользователя'
    )

    def set_invite_code(self) -> None:
        """
        Функция генерирует случайный инвайт-код для пользователя
        и сохраняет его в поле 'invite_code'
        """
        chars = string.ascii_letters + string.digits
        code = ''.join(random.sample(chars, 6))
        self.invite_code = code
        self.save()

    def __str__(self) -> str:
        """Строковое представление модели пользователя"""
        return f'Пользователь #{self.pk}, тел. {self.phone_number}'

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['-pk']
