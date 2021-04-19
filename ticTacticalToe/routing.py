from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'(?P<game_name>\w+)/[A-Za-z]{1,150}/$', consumers.UserSocketConsumer.as_asgi()),
]
