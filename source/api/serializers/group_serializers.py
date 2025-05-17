from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from source.api.models import User, Group
from source.api.serializers.user_serializers import UserReadSerializer


class GroupBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'created']
        extra_kwargs = {
            'id': {'read_only': True},
            'created': {'read_only': True}
        }

    def validate_name(self, value):
        queryset = Group.objects.filter(name__iexact=value)

        if hasattr(self, 'instance') and self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        
        if queryset.exists():
            raise serializers.ValidationError("Группа с таким названием уже существует")
        
        return value


class GroupNameOnlyReadSerializer(GroupBaseSerializer):
    class Meta(GroupBaseSerializer.Meta):
        fields = ['id', 'name']
        read_only_fields = fields


class GroupReadSerializer(GroupBaseSerializer):
    author = UserReadSerializer(read_only=True)
    messages = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    members = serializers.SerializerMethodField()

    class Meta(GroupBaseSerializer.Meta):
        fields = GroupBaseSerializer.Meta.fields + ['author', 'members', 'messages']
        read_only_fields = fields

    def get_members(self, obj):
    # Делаем только в чтении, тк в остальных случаях нужно явно указывать автора
        members = obj.members.all()
        members_data = UserReadSerializer(members, many=True).data

        if obj.author and obj.author not in members:
            author_data = UserReadSerializer(obj.author).data
            members_data.append(author_data)

        return members_data


class GroupCreateSerializer(GroupBaseSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    """
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    """
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False
    )

    class Meta(GroupBaseSerializer.Meta):
        fields = GroupBaseSerializer.Meta.fields + ['author', 'members']

    def validate(self, data):
        members = data.get('members', [])
        if len(members) < 1:
            raise serializers.ValidationError(
                {"members": "Нельзя создать группу с одним участником"}
            )
        return data

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        group = Group.objects.create(**validated_data)
        group.members.set(members)
        return group


class GroupUpdateSerializer(GroupBaseSerializer):
    class Meta(GroupBaseSerializer.Meta):
        fields = GroupBaseSerializer.Meta.fields
        extra_kwargs = {
            'name': {
                'validators': [],
            }
        }

    def validate(self, data):
        if 'name' in data:
            queryset = Group.objects.filter(name__iexact=data['name'])
            if hasattr(self, 'instance') and self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    {"name": "Группа с таким названием уже существует"}
                )
        return data


class GroupAddMemberSerializer(serializers.Serializer):
    group_id = serializers.IntegerField(required=True)
    members_id = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=True
    )

    def validate(self, data):
        try:
            group = Group.objects.get(id=data['group_id'])
        except Group.DoesNotExist:
            raise ValidationError("Группа не найдена")

        current_user = self.context['request'].user
        if not (current_user == group.author or current_user in group.members.all()):
            raise PermissionDenied("Только автор и участники группы могут добавлять новых членов")

        existing_members = group.members.filter(id__in=[user.id for user in data['members_id']])
        if existing_members.exists():
            raise ValidationError(
                f"Некоторые пользователи уже состоят в группе: {list(existing_members.values_list('id', flat=True))}"
            )

        data['group'] = group
        return data

    def save(self, **kwargs):
        group = self.validated_data['group']
        members_to_add = self.validated_data['members_id']
        group.members.add(*members_to_add)
        return group

# TO DO Подумать над реализацией
class GroupRemoveMemberSerializer(serializers.Serializer):
    members_id = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=True,
        help_text="Список ID участников для удаления"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = self.context.get('group')
        self.request = self.context.get('request')
        
        if not self.request or not hasattr(self.request, 'user'):
            raise PermissionDenied("Требуется аутентификация")
        
        if self.group:
            self.current_user = self.request.user
            self._validate_group_author()
            self.member_ids = set(
                self.group.members.values_list('id', flat=True)
            )

    def _validate_group_author(self):
        if not hasattr(self.group, 'author'):
            raise ValidationError("Группа не имеет указанного автора")
        
        if self.current_user != self.group.author:
            raise PermissionDenied("Только автор группы может удалять участников")

    def validate_members_id(self, value):
        if not value:
            raise ValidationError("Необходимо указать хотя бы одного участника")

        if self.current_user.id in value:
            raise ValidationError("Нельзя удалить самого себя из группы")

        return value

    def validate(self, data):
        input_ids = set(data['members_id'])

        invalid_ids = input_ids - self.member_ids
        if invalid_ids:
            raise ValidationError(
                f"Пользователи с ID {invalid_ids} не являются участниками группы"
            )

        users = User.objects.filter(id__in=data['members_id'])
        if len(users) != len(data['members_id']):
            found_ids = {u.id for u in users}
            missing_ids = set(data['members_id']) - found_ids
            raise ValidationError({
                'members_id': f"Пользователи с ID {missing_ids} не найдены"
            })
        
        data['users'] = users
        return data

    def save(self, **kwargs):
        users_to_remove = self.validated_data['users']
        self.group.members.remove(*users_to_remove)

        return {
            'group_id': self.group.id,
            'removed_members': [user.id for user in users_to_remove],
            'remaining_members_count': self.group.members.count()
        }


class GroupDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)

    def validate(self, data):
        if not Group.objects.filter(id=data['id']).exists():
            raise serializers.ValidationError("Группа не найдена")
        return data

    def delete(self):
        Group.objects.filter(id=self.validated_data['id']).delete()