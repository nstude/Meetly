from django.db import models  
from django.contrib.auth.models import User  

class Profile(models.Model): # Профиль пользователя 
    user = models.OneToOneField( # Модель юзера
        User,
        on_delete=models.CASCADE
    )
    friends = models.ManyToManyField( # Друзья
        User,
        related_name='profile'
    )
    bio = models.TextField( # Биография
        blank=True
    )
    gender = models.CharField( # Пол (гендер) - male/female
        max_length=10
    )

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'

class Category(models.Model):  # Категория поста
    name = models.CharField( # Название
        max_length=100
    )
    description = models.TextField( # Описание
        blank=True
    )

    def __str__(self):
        return self.name

class Post(models.Model):  # Пост
    author = models.ForeignKey( # Автор
        User,
        related_name='posts',
        on_delete=models.CASCADE
    )
    category = models.ForeignKey( # Категория
        Category,
        related_name='posts',
        on_delete=models.SET_NULL, null=True
    )
    title = models.CharField( # Название
        max_length=200
    )
    text = models.TextField() # Текст
    created = models.DateTimeField( # Дата создания
        auto_now_add=True
    )
    updated = models.DateTimeField( # Дата обновления
        auto_now=True
    )
    likes = models.ManyToManyField( # Кол-во лайков
        User,
        related_name='liked_posts',
        blank=True
    )

    class Meta:
        ordering = ['-published']

    def __str__(self):
        return self.title

class Comment(models.Model):  # Коменты
    post = models.ForeignKey(  # Пост, к которому относится комент
        Post,
        related_name='comments',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(User, # Автор комента
        related_name='comments',
        on_delete=models.CASCADE
    )
    text = models.TextField() # Текст комента
    created = models.DateTimeField( # Дата создания
        auto_now_add=True
    )

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f'Комментарий от {self.author.username} на {self.post.title}'

class Group(models.Model):  # Группа
    author = models.ForeignKey(User, # Автор
        related_name='groups',
        on_delete=models.CASCADE
    )
    name = models.CharField( # Название группы
        max_length=100
    )
    members = models.ManyToManyField( # Члены группы
        User,
        related_name='groups'
    )
    created = models.DateTimeField( # Дата создания
        auto_now_add=True
    )

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f'Группа {self.name}'
    
class Community(models.Model):  # Сообщество
    author = models.ForeignKey(User, # Автор
        related_name='communitys',
        on_delete=models.CASCADE
    )
    name = models.CharField( # Название сообщества
        max_length=100
    )
    members = models.ManyToManyField( # Члены сообщества
        User,
        related_name='communitys'
    )
    title = models.TextField() # Описание
    posts = models.ManyToManyField( # Посты
        Post,
        related_name='communitys'
    )
    created = models.DateTimeField( # Дата создания
        auto_now_add=True
    )

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f'Сообщество {self.name}'