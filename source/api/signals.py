from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from .models import Profile, Like 

# -------- User -------- 
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs): # Создает записи в бд при создании нового пользователя
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs): # Создает записи в бд при каждом сохранении пользователя
    instance.profile.save()


# -------- Like -------- 
@receiver(post_save, sender=Like)
def like_created(sender, instance, created, **kwargs):
    if created:
        instance.content_object.likes += 1
        instance.content_object.save()

@receiver(post_delete, sender=Like)
def like_deleted(sender, instance, **kwargs):
    local_content_object = instance.content_object
    if instance is not None and hasattr(local_content_object, 'likes'):
        instance.content_object.likes -= 1
        instance.content_object.save()
