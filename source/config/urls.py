from django.urls import path
from api.views import (
    ProfileListCreateView, ProfileRetrieveUpdateDestroyView,
    PostListCreateView, PostRetrieveUpdateDestroyView,
    GroupListCreateView, GroupRetrieveUpdateDestroyView,
    MessageListCreateView, MessageRetrieveUpdateDestroyView,
    LikeListCreateView, LikeRetrieveUpdateDestroyView
)

urlpatterns = [
    # Маршруты для Profile
    path('profiles/', ProfileListCreateView.as_view(), name='profile-list-create'),
    path('profiles/<int:pk>/', ProfileRetrieveUpdateDestroyView.as_view(), name='profile-retrieve-update-destroy'),

    # Маршруты для Post
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostRetrieveUpdateDestroyView.as_view(), name='post-retrieve-update-destroy'),

    # Маршруты для Group
    path('groups/', GroupListCreateView.as_view(), name='group-list-create'),
    path('groups/<int:pk>/', GroupRetrieveUpdateDestroyView.as_view(), name='group-retrieve-update-destroy'),

    # Маршруты для Message
    path('messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<int:pk>/', MessageRetrieveUpdateDestroyView.as_view(), name='message-retrieve-update-destroy'),

    # Маршруты для Like
    path('likes/', LikeListCreateView.as_view(), name='like-list-create'),
    path('likes/<int:pk>/', LikeRetrieveUpdateDestroyView.as_view(), name='like-retrieve-update-destroy'),
]