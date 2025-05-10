from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

from source.api.models import User, Group
from source.api.serializers.user_serializers import UserReadSerializer


class GroupForUserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']
        read_only_fields = fields


# Делаем только в чтении, тк в остальных случаях нужно явно указывать автора
class GroupReadSerializer(serializers.ModelSerializer):
    author = UserReadSerializer(read_only=True)
    messages = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    members = serializers.SerializerMethodField()
    class Meta:
        model = Group
        fields = ['id', 'name', 'author', 'members', 'created', 'messages']
        read_only_fields = fields

    def get_members(self, obj):
        members = obj.members.all()
        members_data = UserReadSerializer(members, many=True).data

        if obj.author and obj.author not in members:
            author_data = UserReadSerializer(obj.author).data
            members_data.append(author_data)

        return members_data


class GroupCreateSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'author', 'members']

    def validate_name(self, value):
        if Group.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Группа с таким названием уже существует")
        return value
    
    def validate_members(self, members_data):
        if len(members_data) < 1:
            raise serializers.ValidationError("Нельзя создать группу с одним участников")
        return members_data


class GroupUpdateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'members']

    def validate_name(self, value):
        if Group.objects.filter(name__iexact=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("Группа с таким названием уже существует")
        return value
    
    def validate_members(self, members_data):
        if len(members_data) < 1:
            raise serializers.ValidationError("В группе не может остаться меньше двух участников")
        return members_data
# TO DO При обновлении списка юзеров не переписывать всех заново, а удалять/добавлять по одному
# Возможно реализовать через два отдельных эндпоинта (на удаление и на добавление),
# причём, чтобы id можно было задавать списком.

class GroupDeleteSerializer(serializers.Serializer): 
    id = serializers.IntegerField(required=True)

    def validate(self, data):
        try:
            Group.objects.get(id=data['id'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Группа не найдена")

        return data

    def delete(self):
        group = Group.objects.get(id=self.validated_data['id'])
        group.delete()
        return