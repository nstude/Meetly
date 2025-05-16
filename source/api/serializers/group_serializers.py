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
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'group' in self.context:
            self.member_ids = set(
                self.context['group'].members.values_list('id', flat=True)
            )
            self.group = self.context['group']

    def validate_user_ids(self, value):
        if not value:
            raise serializers.ValidationError("Необходимо указать хотя бы одного участника")

        input_ids = set(value)
        invalid_ids = input_ids - self.member_ids
        if invalid_ids:
            raise serializers.ValidationError(
                f"Пользователи с ID {invalid_ids} не являются участниками группы"
            )

        return list(input_ids)

    def validate(self, data):
        users = User.objects.filter(id__in=data['user_ids'])
        if len(users) != len(data['user_ids']):
            found_ids = {u.id for u in users}
            missing_ids = set(data['user_ids']) - found_ids
            raise serializers.ValidationError({
                'user_ids': f"Пользователи с ID {missing_ids} не найдены"
            })
        
        data['users'] = users
        return data


class GroupDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)

    def validate(self, data):
        if not Group.objects.filter(id=data['id']).exists():
            raise serializers.ValidationError("Группа не найдена")
        return data

    def delete(self):
        Group.objects.filter(id=self.validated_data['id']).delete()