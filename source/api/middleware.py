import jwt
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login  


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
        for allowed_path in ALLOWED_PATHS:
            if path.startswith(allowed_path):
                return None  
        if request.user.is_authenticated:
            return None

        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = None

        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user = User.objects.get(id=payload['user_id'])
                user = authenticate(request, username=user.username, password=None)
                if user is not None:
                  login(request, user)
                request.user = user  
                return None  

            except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
                pass  
            
        return redirect(reverse('login') + '?next=' + request.path)