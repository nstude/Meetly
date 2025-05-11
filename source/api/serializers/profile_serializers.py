from rest_framework import serializers

from source.api.models import Profile
from .user_serializers import (
    UserReadSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserDeleteSerializer
)

MIN_AGE = 1
MAX_AGE = 200


class ProfileBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'age', 'gender', 'birth_date', 'photo']
        extra_kwargs = {
            'id': {'read_only': True},
            'age': {'required': False},
            'gender': {'required': False},
            'photo': {'required': False}
        }
    
    def validate_age(self, value):
        if value < MIN_AGE or value > MAX_AGE:
            raise serializers.ValidationError("Некорректное значение возраста")
        return value


class ProfileReadSerializer(ProfileBaseSerializer):
    user = UserReadSerializer(read_only=True)
    friends = UserReadSerializer(many=True, read_only=True)

    class Meta(ProfileBaseSerializer.Meta):
        fields = ProfileBaseSerializer.Meta.fields + ['user', 'friends']
        read_only_fields = fields


class ProfileCreateSerializer(ProfileBaseSerializer):
    user = UserCreateSerializer()

    class Meta(ProfileBaseSerializer.Meta):
        fields = ProfileBaseSerializer.Meta.fields + ['user']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserCreateSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        
        return Profile.objects.create(user=user, **validated_data)


# TO DO Сделать добавление друзей как при добавлении юзера в группу
class ProfileUpdateSerializer(ProfileBaseSerializer):
    user = UserUpdateSerializer(required=False)
    friends = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Profile.objects.all(),
        required=False
    )

    class Meta(ProfileBaseSerializer.Meta):
        fields = ProfileBaseSerializer.Meta.fields + ['user', 'friends']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        instance = super().update(instance, validated_data)

        if user_data:
            user_serializer = UserUpdateSerializer(instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        
        return instance

class ProfileDeleteSerializer(ProfileBaseSerializer):
    user = UserDeleteSerializer(required=False)

    class Meta(ProfileBaseSerializer.Meta):
        fields = ['id']

    def validate(self, data):
        if not Profile.objects.filter(id=data['id']).exists():
            raise serializers.ValidationError("Профиль не найден")
        return data

    def delete(self):
        profile = Profile.objects.get(id=self.validated_data['id'])
        user = profile.user
        profile.delete()
        user.delete()