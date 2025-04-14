from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import Profile, Post, Group, Message, Like


User = get_user_model()


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    friends = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user', 'photo', 'photo_url', 'gender', 'birth_date', 'friends']
        extra_kwargs = {'photo': {'write_only': True}}

    def get_friends(self, obj):
        return ProfileShortSerializer(obj.friends.all(), many=True).data

    def get_photo_url(self, obj):
        if obj.photo:
            return obj.photo.url
        return None


class ProfileShortSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    photo_url = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = ['id', 'username', 'photo_url', 'gender']

    def get_photo_url(self, obj):
        if obj.photo:
            return obj.photo.url
        return None


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Like
        fields = ['id', 'user', 'content_type', 'object_id', 'timestamp']
        
    def validate(self, data):
        model_class = data['content_type'].model_class()
        if not model_class.objects.filter(pk=data['object_id']).exists():
            raise serializers.ValidationError("Объект не существует")
        return data


class LikeShortSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Like
        fields = ['id', 'user', 'timestamp']


class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    like_list = LikeShortSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'published', 'likes', 'like_list']
        read_only_fields = ['published', 'likes']



class GroupSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    members = UserShortSerializer(many=True, read_only=True)
    members_count = serializers.IntegerField(source='members.count', read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'author', 'created', 'members', 'members_count']
        read_only_fields = ['created']



class MessageSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    like_list = LikeShortSerializer(many=True)

    class Meta:
        model = Message
        fields = ['id', 'author', 'content', 'timestamp', 'group', 'post', 'likes', 'like_list']
        read_only_fields = ['timestamp', 'likes', 'like_list']

    def validate(self, data):
        if data.get('group') and data.get('post'):
            raise serializers.ValidationError(
                "Сообщение должно быть связано либо с группой, либо с постом, но не с обоими."
            )
        if not data.get('group') and not data.get('post'):
            raise serializers.ValidationError(
                "Сообщение должно быть связано либо с группой, либо с постом."
            )
        return data
