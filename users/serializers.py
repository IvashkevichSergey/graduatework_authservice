from rest_framework import serializers, status
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


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'phone_number',
                  'invite_code', 'invited_by', 'last_login', 'date_joined')
        model = User


class UserAuthSerializer(serializers.Serializer):
    phone_number = serializers.IntegerField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
