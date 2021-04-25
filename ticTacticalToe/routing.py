from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'lobby/[A-Za-z0-9]{1,150}$', consumers.UserGameLobbyConsumer.as_asgi()),
    url(r'(?P<game_name>\w+)/[A-Za-z0-9]{1,150}/board$', consumers.UserGameBoardSocketConsumer.as_asgi()),
    url(r'(?P<game_name>\w+)/[A-Za-z0-9]{1,150}/room$', consumers.UserGameRoomSocketConsumer.as_asgi()),
]
