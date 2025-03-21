from django.contrib import admin
from .models import Profile, Post, Group, Message, Like

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Group)
admin.site.register(Message)
admin.site.register(Like)