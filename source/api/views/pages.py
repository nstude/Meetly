from django.shortcuts import render
from django.contrib.auth.models import User

from source.api.models import User


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
