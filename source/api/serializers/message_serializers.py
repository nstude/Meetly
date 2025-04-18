from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

from source.api.models import User, Message, Post, Group
from source.api.serializers.user_serializers import UserReadSerializer

class MessageReadSerializer(serializers.ModelSerializer):
    author = UserReadSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    like_list = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'author', 'content', 'timestamp', 'post', 'group', 'likes', 'like_list']
        read_only_fields = fields


class MessageCreateSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
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

    class Meta:
        model = Message
        fields = ['id', 'author', 'content', 'post', 'group']

    def validate(self, data):
        if data.get('group') and data.get('post'):
            raise serializers.ValidationError("Сообщение должно быть связано либо с группой, либо с постом")
        if not data.get('group') and not data.get('post'):
            raise serializers.ValidationError("Сообщение должно быть связано с группой или постом")
        return data
    
    def validate_content(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Сообщение не может быть пустым")
        return value
    
    def create(self, validated_data):
        author = validated_data.get('author')
        content = validated_data.get('content')
        
        if 'post' in validated_data:
            post = validated_data['post']
            message = Message.objects.create(
                author=author,
                content=content,
                post=post
            )
        elif 'group' in validated_data:
            group = validated_data['group']
            message = Message.objects.create(
                author=author,
                content=content,
                group=group
            )

        return message

class MessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content']

    def validate_content(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Сообщение не может быть пустым")
        return value
    

class MessageDeleteSerializer(serializers.Serializer): 
    id = serializers.IntegerField(required=True)

    def validate(self, data):
        try:
            Message.objects.get(id=data['id'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Сообщение не найдено")

        return data

    def delete(self):
        message = Message.objects.get(id=self.validated_data['id'])
        message.delete()
        return