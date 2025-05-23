from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.views import View
from rest_framework.decorators import permission_classes
import json
import logging
from rest_framework.decorators import api_view
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from source.api.models import User, Profile, Post, Group, Message, Like
from source.api.serializers.user_serializers import (
    UserReadSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserDeleteSerializer
)
from source.api.serializers.profile_serializers import (
    ProfileReadSerializer,
    ProfileCreateSerializer,
    ProfileUpdateSerializer,
    ProfileDeleteSerializer,
    ProfileAddFriendsSerializer,
    ProfileRemoveFriendsSerializer
)
from source.api.serializers.post_serializers import (
    PostContentOnlyReadSerializer,
    PostContentWithAuthorReadSerializer,
    PostReadSerializer,
    PostCreateSerializer,
    PostUpdateSerializer,
    PostDeleteSerializer
)
from source.api.serializers.group_serializers import (
    GroupNameOnlyReadSerializer,
    GroupReadSerializer,
    GroupCreateSerializer,
    GroupUpdateSerializer,
    GroupDeleteSerializer,
    GroupAddMemberSerializer,
    GroupRemoveMemberSerializer
)
from source.api.serializers.message_serializers import (
    MessageReadSerializer,
    MessageCreateSerializer,
    MessageUpdateSerializer,
    MessageDeleteSerializer
)
from source.api.serializers.like_serializers import (
    LikeReadSerializer,
    LikeCreateSerializer,
    LikeDeleteSerializer
)


# ---------------- Пользователь ----------------
class IsOwnerOrAdminUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj



def user_delete_fields(data):
    data.pop('id', None)
    data.pop('email', None)
    
    return data


class UserRetrieveView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserReadSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user == instance or request.user.is_superuser:
            return super().retrieve(request, *args, **kwargs)

        serializer = self.get_serializer(instance)
        data = user_delete_fields(serializer.data)
        return Response(data)
        """
        sensitive_fields = ['phone', 'last_login', 'date_joined']
        for field in sensitive_fields:
            filtered_data.pop(field, None)
        """
        


class UserRetrieveAllView(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    serializer_class = UserReadSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['username']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.process_data(serializer.data, request.user)
            return self.get_paginated_response(data)
        
        serializer = self.get_serializer(queryset, many=True)
        data = self.process_data(serializer.data, request.user)
        return Response(data)

    def process_data(self, data, current_user):
        result = []
        for user_data in data:
            if user_data['id'] == current_user.id or current_user.is_superuser:
                result.append(user_data)
            else:
                filtered_data = user_delete_fields(user_data.copy())
                result.append(filtered_data)
        return result

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer

    def perform_update(self, serializer):
        instance = serializer.instance

        if not (self.request.user == instance or self.request.user.is_superuser):
            raise PermissionDenied("Вы не имеете прав для редактирования этого аккаунта")

        serializer.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        self.perform_update(serializer)
        
        return Response(
            {"detail": "Данные успешно обновлены"},
            status=status.HTTP_200_OK
        )

class UserDestroyView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserDeleteSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if not (self.request.user == instance or self.request.user.is_superuser):
            raise PermissionDenied("Вы не имеете прав для удаления этого аккаунта")

        if hasattr(instance, 'is_active'):
            instance.is_active = False
            instance.save()
        else:
            instance.delete()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Аккаунт успешно удален"}, 
            status=status.HTTP_204_NO_CONTENT
        )

# Эндпонит для вывода групп конкретного юзера
# TO DO Сделать по уму
class UserGroupsRetrieveView(generics.ListAPIView):
    serializer_class = GroupNameOnlyReadSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Group.objects.filter(members__id=user_id)

# Эндпонит для вывода постов конкретного юзера
class UserPostsRetrieveView(generics.ListAPIView):
    serializer_class = PostContentOnlyReadSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Post.objects.filter(author__id=user_id)
    


# ---------------- Профиль пользователя  ----------------
def profile_delete_fields(data):
    data.pop('id', None)
    data.pop('age', None)
    data.pop('birth_date', None)
    data['user'].pop('id', None)
    data['user'].pop('email', None)
    
    return data

class ProfileRetrieveView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileReadSerializer
    permission_classes = [IsAuthenticated]  

    def retrieve(self, request, *args, **kwargs):
        profile = self.get_object()
        if request.user != profile.user:
            serializer = self.get_serializer(profile)
            data = profile_delete_fields(serializer.data) 
            return Response(data)
        return super().retrieve(request, *args, **kwargs)

#TO DO для всех пользователей убрать friends, оставить только для своего профиля
class ProfileRetrieveAllView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileReadSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['gender', 'birth_date']
    permission_classes = [IsAuthenticated]  

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())  

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            for profile in data:
                if request.user.id != profile.get('user').get('id'):  
                    profile = profile_delete_fields(profile)
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        for profile in data:
            if request.user.id != profile.get('user').get('id'):  
                profile = profile_delete_fields(profile)
        return Response(data)

class ProfileCreateView(generics.CreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileCreateSerializer

class ProfileUpdateView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileUpdateSerializer
    def get_object(self):
        profile_id = self.kwargs['pk']
        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            raise PermissionDenied("Профиль не найден.")
        if profile.user != self.request.user:
            raise PermissionDenied("Вы можете изменить только свой профиль.")
        return profile

class ProfileDestroyView(generics.DestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileDeleteSerializer
    def get_object(self):
        profile_id = self.kwargs['pk']
        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            raise PermissionDenied("Профиль не найден.")
        if profile.user != self.request.user:
            raise PermissionDenied("Вы можете удалить только свой профиль.")
        return profile

# Эндпонит для вывода постов конкретного юзера
class ProfileFriendsPostsRetrieveView(generics.ListAPIView):
    serializer_class = PostContentWithAuthorReadSerializer

    def get_queryset(self):
        profile_id = self.kwargs['profile_id']
        try:
            profile = Profile.objects.get(id=profile_id)
            friends = profile.friends.all()
            posts = Post.objects.filter(author__profile__in=friends)
            return posts
        except Profile.DoesNotExist:
            return Post.objects.none()


class ProfileAddFriendsView(generics.GenericAPIView):
    serializer_class = ProfileAddFriendsSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = serializer.save()
        
        return Response(
            {
                'status': 'success',
                'message': result['message']
            },
            status=status.HTTP_200_OK
        )

    def get_serializer_context(self):
        return {'request': self.request}


class ProfileRemoveFriendsView(generics.GenericAPIView):
    serializer_class = ProfileRemoveFriendsSerializer

    def post(self, request, profile_id):
        profile = self.get_object()
        serializer = ProfileRemoveFriendsSerializer(
            data=request.data,
            context={'profile': profile}
        )
        serializer.is_valid(raise_exception=True)

        profile.friends.remove(*serializer.validated_data['friends'])
        return Response(
            {"status": "Друзья успешно удалены"},
            status=status.HTTP_200_OK
        )

    def get_object(self):
        return Profile.objects.get(pk=self.kwargs['profile_id'])



# ---------------- Пост ----------------
class PostRetrieveView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostReadSerializer
    def get_queryset(self):
        user = self.request.user
        profile = user.profile
        friends = profile.friends.all()
        allowed_users = [user] + [friend.user for friend in friends]
        return Post.objects.filter(author__in=allowed_users)

class PostRetrieveAllView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostReadSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'published']
    def get_queryset(self):
        user = self.request.user
        profile = user.profile
        friends = profile.friends.all()
        allowed_users = [user] + [friend.user for friend in friends]
        return Post.objects.filter(author__in=allowed_users)

class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer

class PostUpdateView(generics.UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostUpdateSerializer
    def get_object(self):
        user = self.request.user  
        post_id = self.kwargs['pk']  
        post = get_object_or_404(Post, id=post_id)
        if post.author != user:
            raise PermissionDenied("Вы не можете изменять чужие посты.")
        return post

class PostDestroyView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDeleteSerializer
    def get_object(self):
        user = self.request.user  
        post_id = self.kwargs['pk']  
        post = get_object_or_404(Post, id=post_id)
        if post.author != user:
            raise PermissionDenied("Вы не можете удалять чужие посты.")
        return post



# ---------------- Группа ----------------
class GroupRetrieveView(generics.RetrieveAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupReadSerializer
    def get_queryset(self):
        user = self.request.user
        return Group.objects.filter(
            Q(members=user) | Q(author=user)
        ).distinct()

class GroupRetrieveAllView(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupReadSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'author', 'created']
    def get_queryset(self):
        user = self.request.user
        return Group.objects.filter(
            Q(members=user) | Q(author=user)
        ).distinct()

class GroupCreateView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupCreateSerializer

class GroupUpdateView(generics.UpdateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupUpdateSerializer
    def get_object(self):
        user = self.request.user
        group_id = self.kwargs['pk']
        group = get_object_or_404(Group, id=group_id)
        if group.author != user:
            raise PermissionDenied("Вы не можете удалять группы, которые не создавали.")

        return group

class GroupDestroyView(generics.DestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupDeleteSerializer
    def get_object(self):
        user = self.request.user
        group_id = self.kwargs['pk']
        group = get_object_or_404(Group, id=group_id)
        if group.author != user:
            raise PermissionDenied("Вы не можете удалять группы, которые не создавали.")

        return group
    


# TO DO Возможно стоит переделать через метод PUT/PATCH
class GroupAddMembersView(generics.GenericAPIView):
    serializer_class = GroupAddMemberSerializer

    def post(self, request, *args, **kwargs):
        group = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        group.members.add(*serializer.validated_data['members_id'])
        return Response(
            {"status": "Пользователи успешно добавлены"},
            status=status.HTTP_200_OK
        )

    def get_object(self):
        return Group.objects.get(pk=self.kwargs['group_id'])


class GroupRemoveMembersView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupRemoveMemberSerializer

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        
        serializer = self.serializer_class(
            data=request.data,
            context={
                'group': group,
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        
        return Response({
            "status": "success",
            **result
        }, status=status.HTTP_200_OK)



# ---------------- Сообщение ----------------
class MessageRetrieveView(generics.RetrieveAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageReadSerializer
    def get_queryset(self): # для отображения сообщений из групп в которых состоит пользователь
        user = self.request.user
        groups = user.group_memberships.all()
        return Message.objects.filter(group__in=groups)

class MessageRetrieveAllView(generics.ListAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageReadSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'group', 'post', 'timestamp']
    def get_queryset(self):
        user = self.request.user
        groups = user.group_memberships.all()
        return Message.objects.filter(group__in=groups)
    

class MessageCreateView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageCreateSerializer

class MessageUpdateView(generics.UpdateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageUpdateSerializer
    queryset = Message.objects.all()
    serializer_class = MessageDeleteSerializer
    def get_object(self):
        user = self.request.user  
        message_id = self.kwargs['pk'] 
        message = get_object_or_404(Message, id=message_id)
        if message.author != user:
            raise PermissionDenied("Вы не можете удалять чужие сообщения.")
        return message

class MessageDestroyView(generics.DestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageDeleteSerializer
    def get_object(self):
        user = self.request.user  
        message_id = self.kwargs['pk'] 
        message = get_object_or_404(Message, id=message_id)
        if message.author != user:
            raise PermissionDenied("Вы не можете обновлять чужие сообщения.")
        return message



# ---------------- Лайк ----------------
class LikeRetrieveView(generics.RetrieveAPIView):
    queryset = Like.objects.all()
    serializer_class = UserReadSerializer

class LikeRetrieveAllView(generics.ListAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeReadSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'content_type', 'object_id', 'timestamp']

class LikeCreateView(generics.CreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeCreateSerializer

class LikeDestroyView(generics.DestroyAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeDeleteSerializer
    def get_object(self):
        user = self.request.user  
        like_id = self.kwargs['pk']  
        like = get_object_or_404(Like, id=like_id)
        if like.user != user:
            raise PermissionDenied("Вы не можете удалять чужие лайки.")
        return like



# ---------------- Регистрация ----------------

class RegisterView(generics.CreateAPIView):
    serializer_class = ProfileCreateSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            profile = serializer.save()
            
            return Response(
                {
                    "status": "success",
                    "user_id": profile.user.id,
                    "profile_id": profile.id,
                    "message": "Регистрация прошла успешно"
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            if "unique constraint" in str(e).lower():
                return Response(
                    {"error": "Пользователь с такими данными уже существует"},
                    # TO DO Добавить файл с ошибками
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ---------------- Смена пароля ----------------
# TO DO Возможно стоит добавить сериализатор для изменения пароля
# Если добавлять, то явно в new_password задать min_length=8 и max_length=128
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')


        if not user.check_password(old_password):
            return JsonResponse({'detail': 'Неверный старый пароль.'}, status=400)

        if len(new_password) < 8:
            return JsonResponse({'detail': 'Пароль должен быть не менее 8 символов.'}, status=400)

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        return JsonResponse({'success': True})


# ---------------- Логин ----------------
# TO DO добавить сериализатор для логина
# Поменять названия
logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    template_name = 'meetly/login.html'  # Путь к вашему шаблону login.html

    def get(self, request):
        """
        Обрабатывает GET-запросы для отображения формы входа.
        """
        form = AuthenticationForm()
        print("GET request received for login page.")  # Выводим информацию в терминал
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        Обрабатывает POST-запросы для аутентификации пользователя и выдачи JWT.
        """
        print(f"Raw request body: {request.body}") # Добавьте это
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            print(f"POST request received: username={username}, password={password[:3]}***")  # Логируем начало пароля (безопасность)
        except json.JSONDecodeError:
            print("Invalid JSON data received.")
            return JsonResponse({'error': "Invalid JSON data."}, status=400)

        form = AuthenticationForm(request, data={'username': username, 'password': password})
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                # Логируем успешную аутентификацию в терминал
                print(f"User '{user.username}' logged in successfully. Access token (truncated): {access_token[:20]}..., Refresh token (truncated): {refresh_token[:20]}...")

                return JsonResponse({
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'username': user.username,
                })
            else:
                print("AuthenticationForm is valid, but form.get_user() returned None.")
                return JsonResponse({'error': "AuthenticationForm is valid, but no user found."}, status=400)
        else:
            print(f"Invalid login attempt. Form errors: {form.errors}")
            return JsonResponse({'error': "Неверное имя пользователя или пароль."}, status=400)


# ---------------- Страницы ----------------
# TO DO Добавить файл бекенда для аутентификации
def index(request):
    return render(request, 'meetly/index.html')


def change_password_page(request):
    return render(request, 'meetly/change-password.html')


def friends_page(request):
    profile = request.user.profile 
    friends_profiles = profile.friends.all() 
    friends = User.objects.filter(profile__in=friends_profiles)  
    others = User.objects.exclude(profile__in=friends_profiles).exclude(id=request.user.id)  
    context = {
        'friends': friends,
        'others': others,
    }
    return render(request, 'friends.html', context)


class AddFriendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data.get('profile_id')
        if not user_id:
            return Response({'error': 'ID профиля обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            friend_profile = user.profile
            profile = request.user.profile
            if friend_profile in profile.friends.all():
                return Response({'error': 'Этот пользователь уже в списке ваших друзей.'}, status=status.HTTP_400_BAD_REQUEST)
            profile.friends.add(friend_profile)

            return Response({'success': True}, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response({'error': 'Профиль не найден'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Ошибка при добавлении в друзья")
            return Response({'error': 'Произошла ошибка на сервере'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
        


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  
            return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    return Response({
        'username': request.user.username,
        'email': request.user.email
    })