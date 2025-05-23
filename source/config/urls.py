from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from source.api.views import (
    ChangePasswordView, RegisterView, LogoutView, LoginView,
    index,  change_password_page, friends_page, current_user
)

# TO DO Возможно разделить урлы
urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('api/', include('source.api.urls')),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('change-password/', change_password_page, name='change-password-page'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password-api'),
    path('current_user/', current_user, name='current_user'),
    path('meetly/friends/', friends_page, name='friends'),
     
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)