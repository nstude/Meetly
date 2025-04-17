from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from source.api.models import User, Profile, Post, Group, Message, Like
from source.api.serializers.user_serializers import (
    UserReadSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserDeleteSerializer
)
from source.api.serializers.profile_serializers import (
    ProfileReadSerializer,
    ProfileCreateSerializer,
    ProfileUpdateSerializer,
    ProfileDeleteSerializer
)
from source.api.serializers.post_serializers import (
    PostReadSerializer,
    PostCreateSerializer,
    PostUpdateSerializer,
    PostDeleteSerializer
)
from source.api.serializers.group_serializers import (
    GroupReadSerializer,
    GroupCreateSerializer,
    GroupUpdateSerializer,
    GroupDeleteSerializer
)
from source.api.serializers.message_serializers import (
    MessageReadSerializer,
    MessageCreateSerializer,
    MessageUpdateSerializer,
    MessageDeleteSerializer
)
from source.api.serializers.like_serializers import (
    LikeReadSerializer,
    LikeCreateSerializer,
    LikeDeleteSerializer
)


# ---------------- Пользователь ----------------
class UserRetrieveView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserReadSerializer

class UserRetrieveAllView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserReadSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['username', 'email']

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer

class UserDestroyView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserDeleteSerializer


# ---------------- Профиль пользователя  ----------------
class ProfileRetrieveView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileReadSerializer

class ProfileRetrieveAllView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileReadSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['gender', 'birth_date']

class ProfileCreateView(generics.CreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileCreateSerializer

class ProfileUpdateView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileUpdateSerializer

class ProfileDestroyView(generics.DestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileDeleteSerializer



# ---------------- Пост ----------------
class PostRetrieveView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostReadSerializer

class PostRetrieveAllView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostReadSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'published']

class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer

class PostUpdateView(generics.UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostUpdateSerializer

class PostDestroyView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDeleteSerializer



# ---------------- Группа ----------------
class GroupRetrieveView(generics.RetrieveAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupReadSerializer

class GroupRetrieveAllView(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupReadSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'author', 'created']

class GroupCreateView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupCreateSerializer

class GroupUpdateView(generics.UpdateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupUpdateSerializer

class GroupDestroyView(generics.DestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupDeleteSerializer



# ---------------- Сообщение ----------------
class MessageRetrieveView(generics.RetrieveAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageReadSerializer

class MessageRetrieveAllView(generics.ListAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageReadSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'group', 'post', 'timestamp']

class MessageCreateView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageCreateSerializer

class MessageUpdateView(generics.UpdateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageUpdateSerializer

class MessageDestroyView(generics.DestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageDeleteSerializer



# ---------------- Лайк ----------------
class LikeRetrieveView(generics.RetrieveAPIView):
    queryset = Like.objects.all()
    serializer_class = UserReadSerializer

class LikeRetrieveAllView(generics.ListAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeReadSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'content_type', 'object_id', 'timestamp']

class LikeCreateView(generics.CreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeCreateSerializer

class LikeDestroyView(generics.DestroyAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeDeleteSerializer
