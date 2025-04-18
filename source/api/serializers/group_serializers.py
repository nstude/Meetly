from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

from source.api.models import User, Group
from source.api.serializers.user_serializers import UserReadSerializer

class GroupReadSerializer(serializers.ModelSerializer):
    author = UserReadSerializer(read_only=True)
    members = UserReadSerializer(many=True, read_only=True)
    messages = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'author', 'members', 'created', 'messages']
        read_only_fields = fields


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