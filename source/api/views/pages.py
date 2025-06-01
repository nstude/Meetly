import json
import logging

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from rest_framework.decorators import api_view
from rest_framework.response import Response

from source.api.models import User, Profile, Group, Message



logger = logging.getLogger(__name__)

# ---------------- Страницы ----------------

# ---------------- Главная ----------------
# TO DO Добавить файл бекенда для аутентификации
def index_page(request):
    return render(request, 'auth/index.html')


# ---------------- Логин ----------------
def login_page(request):
    return render(request, 'auth/login.html')


# ---------------- Регистраиция ----------------
def register_page(request):
    return render(request, 'auth/register.html')


# ---------------- Смена пароля ----------------
def change_password_page(request):
    return render(request, 'auth/change-password.html')


# ---------------- Профиль ----------------
@login_required
def profile_page(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    return render(request, 'profile.html', {'profile': profile})


# ---------------- Группа ----------------
@login_required
def groups_list(request):
    groups = Group.objects.filter(
        Q(members=request.user) | Q(author=request.user)
    ).distinct()
    return render(request, 'groups/list.html', {'groups': groups})

@login_required
def groups_create(request):
    friends = request.user.profile.friends.all()
    return render(request, 'groups/create.html', {'friends': friends})

@login_required
def group_detail(request, group_id):
    group = Group.objects.get(id=group_id)
    messages = Message.objects.filter(group=group).order_by('-timestamp')[:50]
    return render(request, 'groups/detail.html', {
        'group': group,
        'messages': messages
    })

@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        if request.user in group.members.all() and request.user != group.author:
            group.members.remove(request.user)
            return redirect('groups_list')
    
    return redirect('group_detail', group_id=group.id)


# ---------------- Сообщение ----------------
@login_required
@require_http_methods(["POST"])
def send_message(request, group_id):
    try:
        data = json.loads(request.body)
        group = Group.objects.get(id=group_id)
        Message.objects.create(
            author=request.user,
            group=group,
            content=data['content']
        )
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ---------------- Друзья ----------------
@login_required
def friends_list(request):
    try:
        profile = request.user.profile
        friends = profile.friends.all().select_related('user')

        context = {
            'friends': [friend.user for friend in friends],
            'friends_count': friends.count()
        }

    except Profile.DoesNotExist:
        context = {
            'friends': [],
            'friends_count': 0,
            'error': 'Профиль не найден'
        }

    return render(request, 'profile/friends/list.html', context)

@login_required
def add_friend(request):
    profiles = Profile.objects.exclude(
        Q(user=request.user) | Q(id__in=request.user.profile.friends.all())
    )

    context = {
        'profiles': profiles
    }

    return render(request, 'profile/friends/add.html', context)


