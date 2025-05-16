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
from django.dispatch import receiver
from django.views.decorators.http import require_POST
from django.db.models.signals import post_save
from django.contrib.auth import logout
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
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



# ---------------- Регистрация ----------------
"""class IsProfileOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user"""

class RegisterView(generics.CreateAPIView):
    serializer_class = ProfileCreateSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            profile = serializer.save()
            
            return Response(
                {
                    "status": "success",
                    "user_id": profile.user.id,
                    "profile_id": profile.id,
                    "message": "Регистрация прошла успешно"
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            if "unique constraint" in str(e).lower():
                return Response(
                    {"error": "Пользователь с такими данными уже существует"},
                    # TO DO Добавить файл с ошибками
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ---------------- Смена пароля ----------------
# TO DO Возможно стоит добавить сериализатор для изменения пароля
# Если добавлять, то явно в new_password задать min_length=8 и max_length=128
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')


        if not user.check_password(old_password):
            return JsonResponse({'detail': 'Неверный старый пароль.'}, status=400)

        if len(new_password) < 8:
            return JsonResponse({'detail': 'Пароль должен быть не менее 8 символов.'}, status=400)

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        return JsonResponse({'success': True})


# ---------------- Логин ----------------
# TO DO добавить сериализатор для логина
# Поменять названия
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}!")
            return redirect('index')
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")
    else:
        form = AuthenticationForm()

    return render(request, 'meetly/login.html', {'form': form})


# ---------------- Страницы ----------------
# TO DO Добавить файл бекенда для аутентификации
def index(request):
    return render(request, 'meetly/index.html')


def change_password_page(request):
    return render(request, 'meetly/change-password.html')


def friends_page(request):
    profile = request.user.profile 
    friends_profiles = profile.friends.all() 
    friends = User.objects.filter(profile__in=friends_profiles)  
    others = User.objects.exclude(profile__in=friends_profiles).exclude(id=request.user.id)  
    context = {
        'friends': friends,
        'others': others,
    }
    return render(request, 'friends.html', context)


class AddFriendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data.get('profile_id')
        if not user_id:
            return Response({'error': 'ID профиля обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            friend_profile = user.profile
            profile = request.user.profile
            if friend_profile in profile.friends.all():
                return Response({'error': 'Этот пользователь уже в списке ваших друзей.'}, status=status.HTTP_400_BAD_REQUEST)
            profile.friends.add(friend_profile)

            return Response({'success': True}, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response({'error': 'Профиль не найден'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Ошибка при добавлении в друзья")
            return Response({'error': 'Произошла ошибка на сервере'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
        


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Добавляем refresh token в черный список
            return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)