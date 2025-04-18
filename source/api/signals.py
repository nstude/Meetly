from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Like 

# -------- Like -------- 
@receiver(post_save, sender=Like)
def like_created(sender, instance, created, **kwargs):
    if created:
        local_content_object = instance.content_object
        if instance is not None and hasattr(local_content_object, 'likes'):
            instance.content_object.likes += 1
            instance.content_object.save()

@receiver(post_delete, sender=Like)
def like_deleted(sender, instance, **kwargs):
    local_content_object = instance.content_object
    if instance is not None and hasattr(local_content_object, 'likes'):
        instance.content_object.likes -= 1
        instance.content_object.save()
