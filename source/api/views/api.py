from django import forms
from django.db import transaction
from django.http import JsonResponse
from django.contrib import messages
from django.dispatch import receiver
from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models.signals import post_save

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from source.api.models import User, Profile, Post, Group, Message, Like
from source.api.serializers.auth_serializers import ChangePasswordSerializer
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
    ProfileDeleteSerializer,
    ProfileAddFriendsSerializer,
    ProfileRemoveFriendsSerializer
)
from source.api.serializers.post_serializers import (
    PostContentOnlyReadSerializer,
    PostContentWithAuthorReadSerializer,
    PostReadSerializer,
    PostCreateSerializer,
    PostUpdateSerializer,
    PostDeleteSerializer
)
from source.api.serializers.group_serializers import (
    GroupNameOnlyReadSerializer,
    GroupReadSerializer,
    GroupCreateSerializer,
    GroupUpdateSerializer,
    GroupDeleteSerializer,
    GroupAddMemberSerializer,
    GroupRemoveMemberSerializer
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

# Эндпонит для вывода групп конкретного юзера
# TO DO Сделать по уму
class UserGroupsRetrieveView(generics.ListAPIView):
    serializer_class = GroupNameOnlyReadSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Group.objects.filter(members__id=user_id)

# Эндпонит для вывода постов конкретного юзера
class UserPostsRetrieveView(generics.ListAPIView):
    serializer_class = PostContentOnlyReadSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Post.objects.filter(author__id=user_id)

# ---------------- Смена пароля ----------------
class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.data['old_password']):
            return Response(
                {"error": "Неверный старый пароль"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(serializer.data['new_password']) < 8:
            return JsonResponse({'detail': 'Пароль должен быть не менее 8 символов.'}, status=400)
        
        user.set_password(serializer.data['new_password'])
        user.save()
        
        return Response({"message": "Пароль успешно обновлён"})


# ---------------- Профиль пользователя  ----------------
class ProfileRetrieveView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileReadSerializer
    permission_classes = [IsAuthenticated]  

    def retrieve(self, request, *args, **kwargs):
        profile = self.get_object()
        if request.user != profile.user:
            serializer = self.get_serializer(profile)
            data = serializer.data
            data.pop('friends', None)  
            return Response(data)
        return super().retrieve(request, *args, **kwargs)

#TO DO для всех пользователей убрать friends, оставить только для своего профиля
class ProfileRetrieveAllView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileReadSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['gender', 'birth_date']
    permission_classes = [IsAuthenticated]  

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.request.user != instance.user:
            representation.pop('friends', None)  
        
        return representation

class ProfileCreateView(generics.CreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileCreateSerializer

class ProfileUpdateView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileUpdateSerializer

class ProfileDestroyView(generics.DestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileDeleteSerializer

# Эндпонит для вывода постов конкретного юзера
class ProfileFriendsPostsRetrieveView(generics.ListAPIView):
    serializer_class = PostContentWithAuthorReadSerializer

    def get_queryset(self):
        profile_id = self.kwargs['profile_id']
        try:
            profile = Profile.objects.get(id=profile_id)
            friends = profile.friends.all()
            posts = Post.objects.filter(author__profile__in=friends)
            return posts
        except Profile.DoesNotExist:
            return Post.objects.none()


class ProfileAddFriendsView(generics.GenericAPIView):
    serializer_class = ProfileAddFriendsSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = serializer.save()
        
        return Response(
            {
                'status': 'success',
                'message': result['message']
            },
            status=status.HTTP_200_OK
        )

    def get_serializer_context(self):
        return {'request': self.request}


class ProfileRemoveFriendsView(generics.GenericAPIView):
    serializer_class = ProfileRemoveFriendsSerializer

    def post(self, request, profile_id):
        profile = self.get_object()
        serializer = ProfileRemoveFriendsSerializer(
            data=request.data,
            context={'profile': profile}
        )
        serializer.is_valid(raise_exception=True)

        profile.friends.remove(*serializer.validated_data['friends'])
        return Response(
            {"status": "Друзья успешно удалены"},
            status=status.HTTP_200_OK
        )

    def get_object(self):
        return Profile.objects.get(pk=self.kwargs['profile_id'])



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
    def get_queryset(self):
        user = self.request.user
        profile = user.profile
        friends = profile.friends.all()
        allowed_users = [user] + [friend.user for friend in friends]
        return Post.objects.filter(author__in=allowed_users)

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
    def get_queryset(self):
        user = self.request.user
        return Group.objects.filter(members=user)

class GroupCreateView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupCreateSerializer

class GroupUpdateView(generics.UpdateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupUpdateSerializer

class GroupDestroyView(generics.DestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupDeleteSerializer

# TO DO Возможно стоит переделать через метод PUT/PATCH
class GroupAddMembersView(generics.GenericAPIView):
    serializer_class = GroupAddMemberSerializer

    def post(self, request, *args, **kwargs):
        group = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        group.members.add(*serializer.validated_data['members_id'])
        return Response(
            {"status": "Пользователи успешно добавлены"},
            status=status.HTTP_200_OK
        )

    def get_object(self):
        return Group.objects.get(pk=self.kwargs['group_id'])


class GroupRemoveMembersView(generics.GenericAPIView):
    serializer_class = GroupRemoveMemberSerializer

    def post(self, request, *args, **kwargs):
        group = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={'group': group}
        )
        serializer.is_valid(raise_exception=True)
        
        group.members.remove(*serializer.validated_data['members_id'])
        return Response(
            {"status": "Пользователи успешно удалены"},
            status=status.HTTP_200_OK
        )

    def get_object(self):
        return Group.objects.get(pk=self.kwargs['group_id'])



# ---------------- Сообщение ----------------
class MessageRetrieveView(generics.RetrieveAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageReadSerializer
    def get_queryset(self): # для отображения сообщений из групп в которых состоит пользователь
        user = self.request.user
        groups = user.group_memberships.all()
        return Message.objects.filter(group__in=groups)

class MessageRetrieveAllView(generics.ListAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageReadSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'group', 'post', 'timestamp']
    def get_queryset(self):
        user = self.request.user
        groups = user.group_memberships.all()
        return Message.objects.filter(group__in=groups)
    

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