from rest_framework import serializers

from source.api.models import User, Message, Post, Group
from source.api.serializers.user_serializers import UserReadSerializer


class MessageBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'timestamp']
        extra_kwargs = {
            'id': {'read_only': True},
            'timestamp': {'read_only': True}
        }

    def validate_content(self, value):
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Сообщение не может быть пустым")
        return value


class MessageReadSerializer(MessageBaseSerializer):
    author = UserReadSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    group = serializers.PrimaryKeyRelatedField(read_only=True)
    like_list = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta(MessageBaseSerializer.Meta):
        fields = MessageBaseSerializer.Meta.fields + ['author', 'post', 'group', 'likes', 'like_list']
        read_only_fields = fields

# TO DO Понять, стоит ли перерабатывать отправку сообщений (чтобы id объекта задавался не в теле, а в запросе)
class MessageCreateSerializer(MessageBaseSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    post = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(),
        required=False
    )
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        required=False
    )

    class Meta(MessageBaseSerializer.Meta):
        fields = MessageBaseSerializer.Meta.fields + ['author', 'post', 'group']

    def validate(self, data):
        has_post = 'post' in data and data['post'] is not None
        has_group = 'group' in data and data['group'] is not None
        
        if has_post and has_group:
            raise serializers.ValidationError("Сообщение должно быть связано либо с группой, либо с постом")
        if not has_post and not has_group:
            raise serializers.ValidationError("Сообщение должно быть связано с группой или постом")
        return data

    def create(self, validated_data):
        return Message.objects.create(**validated_data)


class MessageUpdateSerializer(MessageBaseSerializer):
    class Meta(MessageBaseSerializer.Meta):
        fields = ['id', 'content']


class MessageDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)

    def validate(self, data):
        if not Message.objects.filter(id=data['id']).exists():
            raise serializers.ValidationError("Сообщение не найдено")
        return data

    def delete(self):
        Message.objects.get(id=self.validated_data['id']).delete()