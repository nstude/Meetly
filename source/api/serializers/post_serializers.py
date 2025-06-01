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
    author = serializers.SerializerMethodField()
    comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    likes = serializers.IntegerField(read_only=True, source='like_list.count')  
    user_liked = serializers.SerializerMethodField()  
    liked_users_ids = serializers.SerializerMethodField()  

    class Meta(PostContentWithAuthorReadSerializer.Meta):
        fields = PostContentWithAuthorReadSerializer.Meta.fields + ['comments', 'likes', 'user_liked', 'liked_users_ids']  

    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username
        }

    def get_user_liked(self, obj):
        user = self.context['request'].user
        return obj.like_list.filter(user=user).exists()  

    def get_liked_users_ids(self, obj):
        liked_users = obj.like_list.values_list('user__id', flat=True)  
        return liked_users


class PostCreateSerializer(PostBaseSerializer):
    author = serializers.HiddenField(
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
    
    
