from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

from source.api.models import User, Post
from source.api.serializers.user_serializers import UserReadSerializer

# TO DO сделать через наследование
class PostForUserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'content']
        read_only_fields = fields


class PostForFriendsReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'author', 'content']
        read_only_fields = fields


class PostReadSerializer(serializers.ModelSerializer):
    author = UserReadSerializer(read_only=True)
    comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    like_list = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'published', 'likes', 'comments', 'like_list']
        read_only_fields = fields


class PostCreateSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Post
        fields = ['id', 'author', 'content']

    def create(self, validated_data):
        author_data = validated_data.pop('author')
        content_data = validated_data.pop('content')
        post = Post.objects.create(author=author_data, content=content_data)

        return post
    
    def validate_content(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Пост не может быть пустым")
        return value


class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'content']

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.save()

        return instance

    def validate_content(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Пост не может быть пустым")
        return value


class PostDeleteSerializer(serializers.Serializer): 
    id = serializers.IntegerField(required=True)

    def validate(self, data):
        try:
            Post.objects.get(id=data['id'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Пост не найден")

        return data

    def delete(self):
        post = Post.objects.get(id=self.validated_data['id'])
        post.delete()
        return