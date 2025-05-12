from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User
from source.api.models import Profile
from .user_serializers import (
    UserReadSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserDeleteSerializer
)

class ProfileReadSerializer(serializers.ModelSerializer):
    user = UserReadSerializer(read_only=True)
    friends = UserReadSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'photo', 'gender', 'friends', 'birth_date']
        read_only_fields = fields


class ProfileCreateSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()

    class Meta:
        model = Profile
        fields = ['id', 'user', 'gender', 'birth_date']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        profile = Profile.objects.create(user=user, **validated_data)

        return profile


class ProfileUpdateSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer(required=False)
    photo = serializers.ImageField(required=False)
    friends = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Profile.objects.all(),
        required=False
    )

    class Meta:
        model = Profile
        fields = ['id', 'user', 'photo', 'gender', 'birth_date', 'friends']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        instance = super().update(instance, validated_data)

        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        
        return instance


class ProfileDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    user = UserDeleteSerializer(required=False)

    def validate(self, data):
        try:
            user = User.objects.get(id=data['id'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Профиль не найден")

        return data

    def delete(self):
        try:   
            user_id = self.validated_data['user']['id']
            user = User.objects.get(id=user_id)
            user.delete()

            profile_id = self.validated_data['id']
            profile = Profile.objects.get(id=profile_id)
            profile.delete()
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Профиль или пользователь не найдены")
        return