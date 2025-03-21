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
    
    gender = models.CharField( # Пол (гендер) - male/female
        max_length=10
    )
    
    photo = models.CharField( # Фотография
        max_length=100
    )
    login = models.CharField(  # Логин пользователя
        max_length=150,  
        unique=True  
    )
    password = models.CharField(  # Пароль пользователя
        max_length=150,    
    )
    
    birth_date = models.DateField(  # Дата рождения
        blank=True,  # Разрешаем оставлять пустым
        null=True,   # Разрешаем значение NULL в базе данных
    )

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'


class Post(models.Model):  # Пост
    author = models.ForeignKey( # Автор
        User,
        related_name='posts',
        on_delete=models.CASCADE
    )
    id_post = models.AutoField(primary_key=True) # иднетификатор поста
    text = models.TextField() # Текст
    created = models.DateTimeField( # Дата создания
        auto_now_add=True
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


class Group(models.Model):  # Группа
    author = models.ForeignKey(User, # Автор
        related_name='groups',
        on_delete=models.CASCADE
    )
    
    id_group = models.AutoField( # иднетификатор поста
        primary_key=True
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
    
class Message(models.Model):  # Сообщение
    message = models.ForeignKey(  
        Post,
        related_name='likes',
        on_delete=models.CASCADE
    )
    text = models.TextField() # Текст
    author = models.ForeignKey(User, # Автор 
        related_name='likes',
        on_delete=models.CASCADE
    )
    group = models.ForeignKey(User, # Группа 
        related_name='likes',
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(User, # Пост 
        related_name='likes',
        on_delete=models.CASCADE
    )
    
    created = models.DateTimeField( # Дата 
        auto_now_add=True
    )


    def clean(self):
        # Проверяем, сколько полей заполнено
        non_null_fields = sum(1 for field in [self.post, self.group] if field is not None)

        # Если более одного поля не NULL, выбрасываем ошибку
        if non_null_fields > 1:
            raise ValidationError("Только одно из полей может быть заполнено, остальные должны быть NULL.")

    def save(self, *args, **kwargs):
        # Вызываем чистку данных перед сохранением
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f'Лайк от {self.author.username} на {self.post.title}'
    

class Like(models.Model):  # Лайки
    post = models.ForeignKey(  # Пост, к которому относится лайк
        Post,
        related_name='likes',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(User, # Автор 
        related_name='likes',
        on_delete=models.CASCADE
    )
    created = models.DateTimeField( # Дата 
        auto_now_add=True
    )

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f'Лайк от {self.author.username} на {self.post.title}'