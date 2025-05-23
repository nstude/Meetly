import logging

from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

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


# ---------------- Группа ----------------

def groups_list(request):
    groups = Group.objects.filter(members=request.user)
    return render(request, 'groups/list.html', {'groups': groups})


def group_detail(request, group_id):
    group = Group.objects.get(id=group_id)
    messages = Message.objects.filter(group=group).order_by('-timestamp')[:50]
    return render(request, 'groups/detail.html', {
        'group': group,
        'messages': messages
    })


# ---------------- Сообщение ----------------
@require_http_methods(["POST"])
def send_message(request):
    group = Group.objects.get(id=request.POST['group_id'])
    Message.objects.create(
        author=request.user,
        group=group,
        content=request.POST['content']
    )
    return redirect('group_detail', group_id=group.id)


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
