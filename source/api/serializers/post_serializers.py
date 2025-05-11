from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

from source.api.models import User, Post
from source.api.serializers.user_serializers import UserReadSerializer


class PostBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'content', 'published']
        extra_kwargs = {
            'id': {'read_only': True},
            'published': {'read_only': True}
        }
    
    def validate_content(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Пост не может быть пустым")
        return value


class PostContentOnlyReadSerializer(PostBaseSerializer):
    class Meta(PostBaseSerializer.Meta):
        read_only_fields = PostBaseSerializer.Meta.fields


class PostContentWithAuthorReadSerializer(PostBaseSerializer):
    author = UserReadSerializer(read_only=True)

    class Meta(PostBaseSerializer.Meta):
        fields = PostBaseSerializer.Meta.fields + ['author']
        read_only_fields = fields


class PostReadSerializer(PostContentWithAuthorReadSerializer):
    comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    like_list = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    likes = serializers.IntegerField(read_only=True, source='likes.count')

    class Meta(PostContentWithAuthorReadSerializer.Meta):
        fields = PostContentWithAuthorReadSerializer.Meta.fields + ['comments', 'like_list', 'likes']


class PostCreateSerializer(PostBaseSerializer):
    """
    # TO DO Сделать после авторизации
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )"""

    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta(PostBaseSerializer.Meta):
        fields = PostBaseSerializer.Meta.fields + ['author']
        extra_kwargs = {
            **PostBaseSerializer.Meta.extra_kwargs,
            'content': {'required': True}
        }

    def create(self, validated_data):
        return Post.objects.create(**validated_data)


class PostUpdateSerializer(PostBaseSerializer):
    class Meta(PostBaseSerializer.Meta):
        fields = ['id', 'content']

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.save()

        return instance


class PostDeleteSerializer(PostBaseSerializer): 
    
    class Meta(PostBaseSerializer.Meta):
        fields = ['id']

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