from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from source.api.views.pages import friends_page, change_password_page

urlpatterns = [
    path('friends/', friends_page, name='friends-page'),
    path('change-password/', change_password_page, name='change-password-page'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)