from rest_framework import serializers
from django.contrib.auth.models import User, ContentType
from .models import Profile, Post, Group, Message, Like

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Вложенный сериализатор для пользователя
    friends = serializers.PrimaryKeyRelatedField(many=True, queryset=Profile.objects.all())  # Список друзей
    age = serializers.SerializerMethodField()  # Поле для возраста (вычисляемое)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'photo', 'gender', 'friends', 'birth_date', 'age']

    def get_age(self, obj):
        return obj.get_age()


class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Автор поста
    likes = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())  # Список лайков
    total_likes = serializers.SerializerMethodField()  # Поле для общего количества лайков

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'published', 'likes', 'total_likes']

    def get_total_likes(self, obj):
        return obj.total_likes()


class GroupSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Создатель группы
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())  # Участники группы

    class Meta:
        model = Group
        fields = ['id', 'name', 'author', 'members', 'created']


class MessageSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Автор сообщения
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), required=False)  # Группа (необязательно)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), required=False)  # Пост (необязательно)

    class Meta:
        model = Message
        fields = ['id', 'author', 'content', 'timestamp', 'group', 'post']

    def validate(self, data):
        """
        Проверяем, что сообщение связано либо с группой, либо с постом, но не с обоими.
        """
        group = data.get('group')
        post = data.get('post')
        if group and post:
            raise serializers.ValidationError("Сообщение должно быть связано либо с группой, либо с постом, но не с обоими.")
        if not group and not post:
            raise serializers.ValidationError("Сообщение должно быть связано либо с группой, либо с постом.")
        return data


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Пользователь, который поставил лайк
    content_type = serializers.PrimaryKeyRelatedField(queryset=ContentType.objects.all())  # Тип контента (пост, сообщение и т.д.)
    object_id = serializers.IntegerField()  # ID объекта, которому поставили лайк

    class Meta:
        model = Like
        fields = ['id', 'user', 'content_type', 'object_id', 'timestamp']

    def validate(self, data):
        """
        Проверяем, что лайк не дублируется.
        """
        user = data['user']
        content_type = data['content_type']
        object_id = data['object_id']
        if Like.objects.filter(user=user, content_type=content_type, object_id=object_id).exists():
            raise serializers.ValidationError("Вы уже поставили лайк этому объекту.")
        return data