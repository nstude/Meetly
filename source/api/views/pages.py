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
