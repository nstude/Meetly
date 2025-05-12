from django.urls import path, include
from django.contrib import admin
from source.api import views
from django.contrib.auth import views as auth_views
from source.api.views import RegisterUser
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.views import TokenVerifyView
from source.api.views import current_user
from source.api.views import ChangePasswordView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
)

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('polls/', include('source.api.urls')),
    path('register/', views.register, name='register'),
    path('api/register/', RegisterUser.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('api/user/', current_user, name='current_user'),
    path('change-password/', views.change_password_page, name='change-password-page'),
    path('api/change-password/', views.ChangePasswordView.as_view(), name='change-password-api'),
     
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)