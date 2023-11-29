from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    # def create(self, validated_data):
    #     phone_number = validated_data.get('phone_number')
    #     print(phone_number)
    #     user = User.objects.filter(phone_number=phone_number)
    #     print(user)
    #     new_user = User.objects.create(**validated_data)
    #     new_user.save()
    #     print(new_user)
    #     return new_user

    class Meta:
        fields = '__all__'
        model = User


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = User


# class InviteListSerializer(serializers.ModelSerializer):
#     invited_friends = serializers.SerializerMethodField()
#
#     def get_invited_friends(self, obj):
#         friends = User.objects.filter(invited_by=obj).all()
#         res = [friend.phone_number for friend in friends]
#         return res
#
#     class Meta:
#         fields = ('invited_friends',)
#         model = User


class InviteRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        friends = User.objects.filter(invited_by=value).all()
        res = [friend.phone_number for friend in friends]
        return res


class UserDetailSerializer(serializers.ModelSerializer):
    invite_code = serializers.CharField(read_only=True)
    invited_friends = InviteRelatedField(source='invite_code', read_only=True)

    def validate_invited_by(self, value):
        if self.instance.invited_by:
            raise ValidationError(
                'Запрещено изменять код в поле \'invited_by\''
            )
        if self.instance == value:
            raise ValidationError(
                'Запрещено указывать свой инвайт код. '
                'Необходимо указать код пригласившего Вас пользователя'
            )
        return super().validate(value)

    class Meta:
        fields = (
            'id', 'first_name', 'last_name', 'phone_number',
            'invite_code', 'invited_by', 'last_login', 'date_joined', 'invited_friends'
        )
        model = User


class UserAuthSerializer(serializers.Serializer):
    phone_number = serializers.IntegerField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
