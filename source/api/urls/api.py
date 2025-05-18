
from django.urls import path
from source.api.views.api import (
    UserRetrieveAllView,
    UserCreateView,
    UserRetrieveView,
    UserUpdateView,
    UserDestroyView,
    UserGroupsRetrieveView,
    UserPostsRetrieveView
)
from source.api.views.api import (
    ProfileRetrieveAllView,
    ProfileCreateView,
    ProfileRetrieveView,
    ProfileUpdateView,
    ProfileDestroyView,
    ProfileFriendsPostsRetrieveView,
    ProfileAddFriendsView,
    ProfileRemoveFriendsView
)
from source.api.views.api import (
    PostRetrieveAllView,
    PostCreateView,
    PostRetrieveView,
    PostUpdateView,
    PostDestroyView
)
from source.api.views.api import (
    GroupRetrieveAllView,
    GroupCreateView,
    GroupRetrieveView,
    GroupUpdateView,
    GroupDestroyView,
    GroupAddMembersView,
    GroupRemoveMembersView
)
from source.api.views.api import (
    MessageRetrieveAllView,
    MessageCreateView,
    MessageRetrieveView,
    MessageUpdateView,
    MessageDestroyView
)
from source.api.views.api import (
    LikeRetrieveAllView,
    LikeCreateView,
    LikeRetrieveView,
    LikeDestroyView
)
from source.api.views.api import (
    ChangePasswordView
)



urlpatterns = [
    # Маршруты для User
    path('users/', UserRetrieveAllView.as_view(), name='user-retrieve-all'),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/', UserRetrieveView.as_view(), name='user-retrieve'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
    path('users/<int:pk>/delete/', UserDestroyView.as_view(), name='user-destroy'),
    path('users/<int:user_id>/groups/', UserGroupsRetrieveView.as_view(), name='user-groups'), # Эндпоинт для групп юзера
    path('users/<int:user_id>/posts/', UserPostsRetrieveView.as_view(), name='user-posts'), # Эндпоинт для постов юзера
    path('users/change-password/', ChangePasswordView.as_view(), name='change-password'),

    # Маршруты для Profile
    path('profiles/', ProfileRetrieveAllView.as_view(), name='profile-retrieve-all'),
    path('profiles/create/', ProfileCreateView.as_view(), name='profile-create'),
    path('profiles/<int:pk>/', ProfileRetrieveView.as_view(), name='profile-retrieve'),
    path('profiles/<int:pk>/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('profiles/<int:pk>/delete/', ProfileDestroyView.as_view(), name='profile-destroy'),
    path('profiles/<int:profile_id>/friends/posts/', ProfileFriendsPostsRetrieveView.as_view(), name='profile-friends-posts'), # Эндпоинт для постов друзей юзера (профиля)
    path('profiles/<int:profile_id>/friends/add/', ProfileAddFriendsView.as_view(), name='profile-add-friends'),
    path('profiles/<int:profile_id>/friends/remove/', ProfileRemoveFriendsView.as_view(), name='profile-remove-friends'),

    # Маршруты для Post
    path('posts/', PostRetrieveAllView.as_view(), name='post-retrieve-all'),
    path('posts/create/', PostCreateView.as_view(), name='post-create'),
    path('posts/<int:pk>/', PostRetrieveView.as_view(), name='post-retrieve'),
    path('posts/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('posts/<int:pk>/delete/', PostDestroyView.as_view(), name='post-destroy'),

    # Маршруты для Group
    path('groups/', GroupRetrieveAllView.as_view(), name='group-retrieve-all'),
    path('groups/create/', GroupCreateView.as_view(), name='group-create'),
    path('groups/<int:pk>/', GroupRetrieveView.as_view(), name='group-retrieve'),
    path('groups/<int:pk>/update/', GroupUpdateView.as_view(), name='group-update'),
    path('groups/<int:pk>/delete/', GroupDestroyView.as_view(), name='group-destroy'),
    path('groups/<int:group_id>/members/add/', GroupAddMembersView.as_view(), name='group-add-members'),
    path('groups/<int:group_id>/members/remove/', GroupRemoveMembersView.as_view(), name='group-remove-members'),

    # Маршруты для Message
    path('messages/', MessageRetrieveAllView.as_view(), name='message-retrieve-all'),
    path('messages/create/', MessageCreateView.as_view(), name='message-create'),
    path('messages/<int:pk>/', MessageRetrieveView.as_view(), name='message-retrieve'),
    path('messages/<int:pk>/update/', MessageUpdateView.as_view(), name='message-update'),
    path('messages/<int:pk>/delete/', MessageDestroyView.as_view(), name='message-destroy'),

    # Маршруты для Like
    path('likes/', LikeRetrieveAllView.as_view(), name='like-retrieve-all'),
    path('likes/create/', LikeCreateView.as_view(), name='like-create'),
    path('likes/<int:pk>/', LikeRetrieveView.as_view(), name='like-retrieve'),
    path('likes/<int:pk>/delete/', LikeDestroyView.as_view(), name='like-destroy'),
]