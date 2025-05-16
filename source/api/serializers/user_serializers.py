from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied, ValidationError


class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        extra_kwargs = {
            'email': {'required': True}
        }


class UserReadSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        read_only_fields = ('id', 'username', 'email')


class UserCreateSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + ['password']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserUpdateSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        extra_kwargs = {
            **UserBaseSerializer.Meta.extra_kwargs,
            'username': {'required': False},
            'email': {'required': False}
        }
    # TO DO Перенести в views
    def update(self, instance, validated_data):
        if instance != self.context['request'].user and not self.context['request'].user.is_superuser:
            raise PermissionDenied("Вы можете редактировать только свои данные")

        return super().update(instance, validated_data)


class UserDeleteSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        fields = []

    def delete(self):
        user = self.instance
        if hasattr(user, 'is_active'):
            user.is_active = False
            user.save()
        else:
            user.delete()