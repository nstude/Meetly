import json
import logging

from django.db import transaction
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from source.api.serializers.profile_serializers import ProfileCreateSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    return Response({
        'username': request.user.username,
        'email': request.user.email,
        'id':request.user.id
    })


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


# ---------------- Логин ----------------
# TO DO добавить сериализатор для логина
logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    template_name = 'auth/login.html'

    def get(self, request):
        form = AuthenticationForm()
        print("GET request received for login page.")
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        print(f"Raw request body: {request.body}") # Добавьте это
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            print(f"POST request received: username={username}, password={password[:3]}***")
        except json.JSONDecodeError:
            print("Invalid JSON data received.")
            return JsonResponse({'error': "Invalid JSON data."}, status=400)

        form = AuthenticationForm(request, data={'username': username, 'password': password})
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)

                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                print(f"User '{user.username}' logged in successfully. Access token (truncated): {access_token[:20]}..., Refresh token (truncated): {refresh_token[:20]}...")

                return JsonResponse({
                    'access': access_token,
                    'refresh': refresh_token,
                    'username': user.username,
                })
            else:
                print("AuthenticationForm is valid, but form.get_user() returned None.")
                return JsonResponse({'error': "AuthenticationForm is valid, but no user found."}, status=400)
        else:
            print(f"Invalid login attempt. Form errors: {form.errors}")
            return JsonResponse({'error': "Неверное имя пользователя или пароль."}, status=400)


# ---------------- Логаут ----------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            logout(request)

            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

