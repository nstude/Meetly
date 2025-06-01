from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from django.conf.urls.static import static

from source.api.views.auth import current_user
from source.api.views.pages import login_page 

urlpatterns = [
    path('', login_page, name='login_page'),
    path('admin/', admin.site.urls),
    path('api/', include('source.api.urls.api')),
    path('auth/', include('source.api.urls.auth')),
    path('page/', include('source.api.urls.pages')),
    path('token/', include('source.api.urls.token')),
    path('api/user/', current_user, name='current_user'), # TO DO -> source.api.urls.auth
     
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)