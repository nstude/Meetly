from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


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

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserDeleteSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        fields = ['id']

    def validate(self, data):
        if not User.objects.filter(id=data['id']).exists():
            raise serializers.ValidationError("Пользователь не найден")
        return data

    def delete(self):
        user = User.objects.get(id=self.validated_data['id'])
        user.delete()