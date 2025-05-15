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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    return Response({
        'username': request.user.username,
        'email': request.user.email
    })


# ---------------- Регистрация ----------------
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



