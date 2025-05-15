from django.db import transaction
from django.contrib.auth import logout

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from source.api.serializers.profile_serializers import ProfileCreateSerializer
from source.api.serializers.auth_serializers import CustomTokenObtainPairSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    return Response({
        'username': request.user.username,
        'email': request.user.email
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
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ---------------- Логаут ----------------
class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({"message": "Successfully logged out"})

