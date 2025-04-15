from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# ---------------- Профиль пользователя  ----------------
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    photo = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        verbose_name="Фотография профиля"
    )
    gender = models.CharField( # male(m)/female(f)
        max_length=1,
        verbose_name="Пол"
    )
    friends = models.ManyToManyField(
        "self",
        blank=True,
        verbose_name="Друзья"
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Дата рождения"
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return str(self.user.username)

    def get_age(self):
        import datetime
        if self.birth_date:
            today = datetime.date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs): # Создает записи в бд при создании нового пользователя
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs): # Создает записи в бд при каждом сохранении пользователя
    instance.profile.save()


# ---------------- Пост ----------------
class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор"
    )
    content = models.TextField(
        verbose_name="Содержание"
    )
    published = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    likes = models.ManyToManyField(
        User,
        blank=True,
        related_name='liked_posts',
        verbose_name="Лайки"
    )

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ['-published']

    def __str__(self):
        return self.title

    def total_likes(self): # Кол-во лайков
        return self.likes.count()


# ---------------- Группа ----------------
class Group(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название группы"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='author',
        verbose_name="Автор"
    )
    members = models.ManyToManyField(
        User,
        related_name='group_memberships',
        verbose_name="Участники группы"
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
        ordering = ['created']

    def __str__(self):
        return f'Группа {self.name}'


# ---------------- Сообщение ----------------
class Message(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    content = models.TextField(
        verbose_name="Содержание"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время отправки"
    )
    group = models.ForeignKey(Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='messages',
        verbose_name="Группа"
    )
    post = models.ForeignKey(Post, 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comments',
        verbose_name="Пост"
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['timestamp']

    def __str__(self):
        if self.group:
            return f"Сообщение от {self.author.username} в {self.group.name}"
        elif self.post:
            return f"Комментарий от {self.author.username} к посту {self.post.title}"

    def save(self, *args, **kwargs): # Проверяем, что сообщение привязано либо к группе, либо к посту, но не к обоим.
        if self.group and self.post:
            raise ValueError("Сообщение должно быть связано либо с группой, либо с постом, но не с обоими.")
        if not self.group and not self.post:
            raise ValueError("Сообщение должно быть связано либо с группой, либо с постом.")
        super().save(*args, **kwargs)


# ---------------- Лайки ----------------
class Like(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name="Пользователь"
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField(
    )
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время лайка"
    )

    class Meta:
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"
        unique_together = ('user', 'content_type', 'object_id') # Предотвращаем повторные лайки от одного пользователя для одного объекта

    def __str__(self):
        return f"Лайк от {self.user.username} для {self.content_type.model} с ID {self.object_id}"