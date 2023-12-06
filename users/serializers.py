from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import User


class InviteRelatedField(serializers.RelatedField):
    """Сериализатор для формирования списка пользователей,
     приглашённых по одному инвайт-коду"""

    def to_internal_value(self, data):
        pass

    def to_representation(self, value: str) -> list:
        users = User.objects.filter(invited_by=value).all()
        return [friend.phone_number for friend in users]


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя"""
    invite_code = serializers.CharField(read_only=True)
    invited_users = InviteRelatedField(source='invite_code', read_only=True)

    def validate_invited_by(self, value: str) -> super:
        """Валидатор для поля 'invited_by'"""

        # Проверка на изменение ранее введённого инвайт-кода
        if self.instance.invited_by:
            raise ValidationError(
                'Запрещено изменять код в поле \'invited_by\''
            )

        # Проверка на ввод своего собственного инвайт-кода
        if self.instance == value:
            raise ValidationError(
                'Запрещено указывать свой инвайт код. '
                'Необходимо указать код пригласившего Вас пользователя.'
            )
        return super().validate(value)

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'phone_number',
            'invite_code', 'invited_by', 'invited_users',
            'last_login', 'date_joined', 'is_active'
        )


class UserAuthSerializer(serializers.Serializer):
    """Сериализатор для валидации номера телефона при
    авторизации пользователя"""
    phone_number = serializers.IntegerField()

    def validate_phone_number(self, value):
        """Валидатор для поля phone_number"""

        if len(str(value)) != 11:
            raise ValidationError(
                "Проверьте количество символов в номере. "
                "Номер телефона должен быть указан в формате 8XXXXXXXXXX")

        if not str(value).startswith('8'):
            raise ValidationError(
                "Номер телефона должен начинаться с цифры 8")

        return super(UserAuthSerializer, self).validate(value)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CodeAuthSerializer(serializers.Serializer):
    """Сериализатор для валидации кода авторизации пользователя"""
    verification_code = serializers.IntegerField()

    def validate_verification_code(self, value):
        """Валидатор для поля verification_code"""

        if len(str(value)) != 4:
            raise ValidationError(
                "Код авторизации должен содержать 4 цифры"
            )

        return super(CodeAuthSerializer, self).validate(value)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
