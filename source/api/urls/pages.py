from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from source.api.views.auth import ChangePasswordView
from source.api.views.pages import friends_page

urlpatterns = [
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password-api'),
    path('meetly/friends/', friends_page, name='friends'),
     
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)