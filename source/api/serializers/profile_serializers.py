from rest_framework import serializers

from source.api.models import User, Profile
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

# TO DO Сделать подтверждение добавления в друзья
class ProfileAddFriendsSerializer(serializers.Serializer):
    friends_id = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Profile.objects.all(),
        required=True
    )

    def validate_friends_id(self, value):
        if not value:
            raise serializers.ValidationError("Необходимо указать хотя бы одного друга")

        if self.context['request'].user.profile.id in [p.id for p in value]:
            raise serializers.ValidationError("Нельзя добавить самого себя в друзья")
        
        unique_ids = set()
        duplicate_ids = set()
        
        for profile in value:
            if profile.id in unique_ids:
                duplicate_ids.add(profile.id)
            unique_ids.add(profile.id)
            
        if duplicate_ids:
            raise serializers.ValidationError(f"Нельзя добавлять одного человека несколько раз. Дубликаты: {', '.join(map(str, duplicate_ids))}")

        existing_friends = set(
            self.context['request'].user.profile.friends.filter(id__in=unique_ids).values_list('id', flat=True)
        )
        
        if existing_friends:
            raise serializers.ValidationError(f"Эти пользователи уже у вас в друзьях: {', '.join(map(str, existing_friends))}")

        return value

# TO DO Подумать над реализацией
# Возможно есть дргуие пути, которые не учтены
class ProfileRemoveFriendsSerializer(serializers.Serializer):
    friends_id = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'profile' in self.context:
            self.friend_ids = set(self.context['profile'].friends.values_list('id', flat=True))
            self.profile_id = self.context['profile'].id

    def validate_friends_id(self, value):
        if not value:
            raise serializers.ValidationError("Необходимо указать хотя бы одного друга")

        if self.profile_id in value:
            raise serializers.ValidationError("Нельзя удалить самого себя из друзей")

        input_ids = set(value)

        invalid_ids = input_ids - self.friend_ids
        if invalid_ids:
            raise serializers.ValidationError(
                f"ID {invalid_ids} не найдены среди ваших друзей"
            )
        
        return list(input_ids)

    def validate(self, data):
        friends = Profile.objects.filter(id__in=data['friends_id'])
        if len(friends) != len(data['friends_id']):
            found_ids = {f.id for f in friends}
            missing_ids = set(data['friends_id']) - found_ids
            raise serializers.ValidationError({
                'friends_id': f"Профили с ID {missing_ids} не найдены"
            })
        
        data['friends'] = friends
        return data


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