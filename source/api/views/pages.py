from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login

from source.api.models import User, Group, Message

import logging
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
def friends_list(request):
    return render(request, 'profile/friends/list.html')


def add_friend(request):
    return redirect('friends-list')


def remove_friend(request, friend_id):
    return redirect('friends-list')

"""class AddFriendView(APIView):
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
            logger = logging.getLogger(name)
            logger.exception("Ошибка при добавлении в друзья")
            return Response({'error': 'Произошла ошибка на сервере'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)"""