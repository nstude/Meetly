import os
import sys
import django
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "source.config.settings")

django.setup()

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from source.api.models import Profile, Post, Group, Message, Like
from datetime import datetime, timedelta


def create_users(num_users):
    for num_user in range(num_users):
        if not User.objects.filter(username=f'user{num_user}').exists():
            user = User.objects.create_user(
                username=f'user{num_user}',
                password='password123',
                email=f'user{num_user}@example.com'
            )
            print(f'Юзер {num_user} был успешно создан.')
        else:
            print(f'Юзер {num_user} уже существует.')
    return


def create_profiles(users):
    for user in users:
        if not Profile.objects.filter(user=user).exists():
            Profile.objects.create(
                user=user,
                gender=random.choice(['m', 'f']),
                birth_date=datetime.today() - timedelta(days=random.randint(18 * 365, 50 * 365)),
                photo=None
            )
            print(f'Профиль для {user.username} был успешно создан.')
        else:
            print(f'Профиль для {user.username} уже существует.')
    return


def create_groups(users, num_groups):
    for num_group in range(num_groups):
        group_name = name=f"Группа {num_group}"
        if not Group.objects.filter(name=group_name).exists():
            group = Group.objects.create(
                group_name,
                author=random.choice(users),
                created=datetime.now() - timedelta(days=random.randint(0, 30))
            )
            members = random.sample(users, random.randint(2, 5))
            group.members.add(*members)
            print(f'Группа {group_name} была успешно создана.')
        else:
            print(f'Группа c названием {group_name} уже существует.')
    return


def create_posts(users, num_posts):
    for num_post in range(num_posts):
        post = Post.objects.create(
            author=random.choice(users),
            content=f"Содержание поста #{num_post}",
            published=datetime.now() - timedelta(days=random.randint(0, 30))
        )
        print(f'Пост с ID {post.id} был успешно создан.')
    return


def create_messages_for_object(users, objects, num_messages):
    for num_message in range(num_messages):
        object = random.choice(objects)

        if objects.model is Post:
            Message.objects.create(
                author=random.choice(users),
                content=f"Комментарий к посту {object.id}",
                post=object,
                timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
            )
            print(f'Комментарий к посту с ID {object.id} был успешно создан.')
        elif objects.model is Group:
            Message.objects.create(
                author=random.choice(users),
                content=f"Сообщение в группе {object.name}",
                group=object,
                timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
            )
            print(f'Сообщение в группе {object.name} было успешно создано.')
        else:
            print("Передан некорректный тип модели")
    return


def create_messages_for_groups_and_posts(users, groups, posts, num_messages):
    create_messages_for_object(users, groups, num_messages)
    create_messages_for_object(users, posts, num_messages)


def create_likes_for_object(users, object_type, objects):
    content_type_object = ContentType.objects.get_for_model(object_type)
    user=random.choice(users)
    for object in objects:
        if not Like.objects.filter(
            user=user,
            content_type=content_type_object,
            object_id=object.id
        ).exists():
            Like.objects.create(
                user=user,
                content_type=content_type_object,
                object_id=object.id
            )
            print(f'Лайк к объекту {object} был успешно создан.')
        else:
            print(f'Лайк к объекту {object} уже существует.')
    return


def create_like_for_message_and_posts(users, posts, messages):
    create_likes_for_object(users, Post, posts)
    create_likes_for_object(users, Message, messages)
    return


def populate_db_with_test_values():
    create_users(10)
    users = list(User.objects.all())

    create_profiles(users)
    create_groups(users, 5)
    create_posts(users, 10)

    groups = Group.objects.all()
    messages = Message.objects.all()
    posts = Post.objects.all()

    create_messages_for_groups_and_posts(users, groups, posts, 10)
    create_like_for_message_and_posts(users, posts, messages)


def delete_all_test_records_in_object(object):
    object.objects.all().delete()


def delete_all_objects():
    delete_all_test_records_in_object(Like)
    delete_all_test_records_in_object(Message)
    delete_all_test_records_in_object(Post)
    delete_all_test_records_in_object(Group)
    delete_all_test_records_in_object(Profile)
    delete_all_test_records_in_object(User)


if __name__ == '__main__':
    populate_db_with_test_values()
    #delete_all_objects()
