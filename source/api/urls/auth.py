from django.conf import settings
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

from source.api.views.auth import (
    RegisterView,
    login_view
)

from source.api.views.pages import change_password_page

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('change-password/', change_password_page, name='change-password-page'),
]