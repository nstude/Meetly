import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from api.models import Profile, Post, Group, Message, Like
from datetime import datetime, timedelta


# Функция для создания тестовых пользователей
def create_users(num_users):
    users = []
    for i in range(num_users):
        if not User.objects.filter(username=f'user{i}').exists():
            user = User.objects.create_user(
                username=f'user{i}',
                password='password123',
                email=f'user{i}@example.com'
            )
            users.append(user)
        else:
            print(f'Юзер {f'user{i}'} уже существует.')
            users.append(User.objects.get(username=f'user{i}'))
    return users

def create_profiles(users):
    for user in users:
        # Проверяем, существует ли уже профиль для данного пользователя
        if not Profile.objects.filter(user=user).exists():
            # Создаем профиль, если его нет
            profile = Profile.objects.create(
                user=user,
                gender=random.choice(['m', 'f']),
                birth_date=datetime.today() - timedelta(days=random.randint(18 * 365, 50 * 365)),  # Возраст от 18 до 50 лет
                photo=None  # Здесь можно подключить фото, если оно есть
            )
            print(f'Профиль для {user.username} был успешно создан.')
        else:
            print(f'Профиль для {user.username} уже существует.')

# Функция для создания групп
def create_groups(users, num_groups):
    for i in range(num_groups):
        if not Group.objects.filter(name=f"Группа {i}").exists():
            group = Group.objects.create(
                name=f"Группа {i}",
                author=random.choice(users),
                created=datetime.now() - timedelta(days=random.randint(0, 30))
            )
            # Добавление участников в группу
            members = random.sample(users, random.randint(1, 5))  # случайное количество участников
            group.members.add(*members)
            print(f'Группа {i} была успешно создана.')
        else:
            print(f'Группа {i} уже существует.')
            

# Функция для создания постов
def create_posts(users, num_posts):
    for i in range(num_posts):
        Post.objects.create(
            author=random.choice(users),
            content=f"Содержание поста #{i}",
            published=datetime.now() - timedelta(days=random.randint(0, 30))
        )


# Функция для создания сообщений
def create_messages(users, groups, posts, num_messages):
    for i in range(num_messages):
        if random.choice([True, False]):
            # Создаем сообщение в группе
            group = random.choice(groups)
            Message.objects.create(
                author=random.choice(users),
                content=f"Сообщение в группе {group.name}",
                group=group,
                timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
            )
        else:
            # Создаем сообщение (комментарий) к посту
            post = random.choice(posts)
            Message.objects.create(
                author=random.choice(users),
                content=f"Комментарий к посту {post.id}",
                post=post,
                timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
            )

# Функция для создания лайков
def create_likes(users, posts, groups):
    for user in users:
        content_type_post = ContentType.objects.get_for_model(Post)
        content_type_group = ContentType.objects.get_for_model(Group)

        # Лайки на постах
        for post in posts:
            if random.choice([True, False]):
                Like.objects.create(
                    user=user,
                    content_type=content_type_post,
                    object_id=post.id,
                    timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
                )

        # Лайки на группах
        for group in groups:
            if random.choice([True, False]):
                Like.objects.create(
                    user=user,
                    content_type=content_type_group,
                    object_id=group.id,
                    timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
                )

# Основная функция для заполнения БД
def populate_db():
    # Создаем пользователей
    users = create_users(10)  # 10 пользователей

    # Создаем профили пользователей
    create_profiles(users)

    # Создаем посты
    create_posts(users, 20)  # 20 постов

    # Создаем группы
    create_groups(users, 5)  # 5 групп

    # Получаем все группы и посты для последующего использования
    groups = Group.objects.all()
    posts = Post.objects.all()

    # Создаем сообщения
    create_messages(users, groups, posts, 50)  # 50 сообщений

    # Создаем лайки
    create_likes(users, posts, groups)

    print("База данных успешно заполнена данными.")

if __name__ == '__main__':
    populate_db()
