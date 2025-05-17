import jwt
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login  
from django.contrib.auth.models import AnonymousUser

ALLOWED_PATHS = [
    reverse('login'),  
    reverse('register'),  
    '/api/token/',  
    '/api/token/refresh/',  
    '/api/token/verify/',  
    '/admin/',  
    '/static/',  
    '/media/',   
]


class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path
        allowed_paths = getattr(settings, 'JWT_ALLOWED_PATHS', [])

        for allowed_path in allowed_paths:
            if path.startswith(allowed_path):
                return None

        if request.user.is_authenticated:
            return None

        auth_header = request.headers.get('Authorization')
        token = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if token:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get('user_id')
                if user_id is not None:
                    user = User.objects.get(id=user_id)
                    request.user = user
                    return None
                    

        # **Ключевое изменение: Не перенаправляем на логин, если мы уже на странице логина**
        if path != reverse('login'):  
            return redirect(reverse('login') + '?next=' + request.path)
        else:
            return None 

        