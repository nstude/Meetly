import jwt
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login  # Import authenticate and login

# Разрешенные пути, которым не требуется авторизация (например, страницы логина и регистрации)
ALLOWED_PATHS = [
    reverse('login'),  # Страница логина (используем reverse для имени URL)
    reverse('register'),  # Страница регистрации (используем reverse для имени URL)
    '/token/',  # API для получения токенов
    '/token/refresh/',  # API для обновления токенов
    '/token/verify/',  # API для проверки токенов
    '/admin/',  # Страница админки
    '/static/',  # Статичные файлы
    '/media/',   # Медиа файлы
]


class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path

        # Разрешаем доступ к разрешённым путям
        for allowed_path in ALLOWED_PATHS:
            if path.startswith(allowed_path):
                return None  # Разрешаем доступ

        # Если пользователь уже аутентифицирован (например, через форму логина), пропускаем JWT-проверку
        if request.user.is_authenticated:
            return None

        # Проверяем наличие токена в заголовке Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = None

        # Если токен есть, пытаемся декодировать его и получить пользователя
        if token:
            try:
                # Декодируем токен
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                # Получаем пользователя из базы данных
                user = User.objects.get(id=payload['user_id'])

                # АУТЕНТИФИЦИРУЕМ И АВТОРИЗИРУЕМ ПОЛЬЗОВАТЕЛЯ
                user = authenticate(request, username=user.username, password=None) # Authenticate the user
                if user is not None:
                  login(request, user)

                request.user = user  # Присваиваем пользователя в request
                return None  # Авторизация прошла успешно

            except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
                pass  # Ошибка декодирования или токен истёк, переходим к редиректу

        # Если пользователь не авторизован, редиректим на страницу логина
        return redirect(reverse('login') + '?next=' + request.path)