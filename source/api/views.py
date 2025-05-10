from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib import messages
from .models import User, Profile, Post, Group, Message, Like
from django import forms
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.response import Response
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

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
    PostForUserReadSerializer,
    PostForFriendsReadSerializer,
    PostReadSerializer,
    PostCreateSerializer,
    PostUpdateSerializer,
    PostDeleteSerializer
)
from source.api.serializers.group_serializers import (
    GroupForUserReadSerializer,
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

# Эндпонит для вывода групп конкретного юзера
# TO DO Сделать по уму
class UserGroupsRetrieveView(generics.ListAPIView):
    serializer_class = GroupForUserReadSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Group.objects.filter(members__id=user_id)

# Эндпонит для вывода постов конкретного юзера
class UserPostsRetrieveView(generics.ListAPIView):
    serializer_class = PostForUserReadSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Post.objects.filter(author__id=user_id)
    


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

# Эндпонит для вывода постов конкретного юзера
class ProfileFriendsPostsRetrieveView(generics.ListAPIView):
    serializer_class = PostForFriendsReadSerializer

    def get_queryset(self):
        profile_id = self.kwargs['profile_id']
        try:
            profile = Profile.objects.get(id=profile_id)
            friends = profile.friends.all()
            posts = Post.objects.filter(author__profile__in=friends)
            return posts
        except Profile.DoesNotExist:
            return Post.objects.none()



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



# TO DO Добавить файл бекенда для аутентификации
def index(request):
    return render(request, 'meetly/index.html')


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Подтверждение пароля')

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают.')
        return password_confirm


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  
            user.set_password(form.cleaned_data['password'])
            user.save() 
            return redirect('index')
    else:
        form = RegistrationForm()

    return render(request, 'meetly/register.html', {'form': form})

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    return Response({
        'username': request.user.username,
        'email': request.user.email
    })

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


def change_password_page(request):
    return render(request, 'meetly/change-password.html')
