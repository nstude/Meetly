from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from source.api.views.pages import (
    login_page,
    index_page,
    register_page,
    change_password_page,
)
from source.api.views.pages import (
    friends_list,
    add_friend    
)
from source.api.views.pages import (
    send_message,
)
from source.api.views.pages import (
    groups_list,
    group_detail,
)

urlpatterns = [
    path('index/', index_page, name='index_page'),
    path('login/', login_page, name='login_page'),
    path('register/', register_page, name='register_page'),
    path('change-password/', change_password_page, name='change_password_page'),

    path('groups/', groups_list, name='groups-list'),
    path('groups/<int:group_id>/', group_detail, name='group-detail'),
    path('groups/<int:group_id>/send/', send_message, name='send-message'),

    path('friends/', friends_list, name='friends_list'),
    path('friends/add/', add_friend, name='add_friends')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)