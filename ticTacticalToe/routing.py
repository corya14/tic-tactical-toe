from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'(?P<game_name>\w+)/[A-Za-z0-9]{1,150}/$', consumers.UserSocketConsumer.as_asgi()),
]
