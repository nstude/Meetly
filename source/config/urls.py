from source.api import views
from source.api.views import current_user, ChangePasswordView

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


# TO DO Возможно разделить урлы
urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('api/', include('source.api.urls')),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/user/', current_user, name='current_user'),
    path('change-password/', views.change_password_page, name='change-password-page'),
    path('api/change-password/', views.ChangePasswordView.as_view(), name='change-password-api'),
    path('meetly/friends/', views.friends_page, name='friends'),
    path('api/add_friend/', views.AddFriendView.as_view(), name='add_friend')
     
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)