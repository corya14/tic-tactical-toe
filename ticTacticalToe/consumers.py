import json
from channels.generic.websocket import WebsocketConsumer
from game.interfaces import BackEndUpdate
from game.interfaces import GameModelInterface
from asgiref.sync import async_to_sync
import logging
authlog = logging.getLogger('auth')
generallog = logging.getLogger('general')


def update_game_lobby(channel_layer):
    async_to_sync(channel_layer.group_send)(
        'lobby',
        {
            "type": "lobby_update",
            "text": json.dumps(GameModelInterface.get_lobby_games()),
        },
    )


def update_gameboard(channel_layer, game_name, frontend_update):
    """Broadcast update to the gameboard for game_name
    """
    async_to_sync(channel_layer.group_send)(
        game_name,
        {
            "type": "frontend_update",
            "text": frontend_update.serialize(),
        },
    )


class UserGameBoardSocketConsumer(WebsocketConsumer):
    """
    Socket consumer for updating the gameboard ONLY
    Client socket onReceive() accepts gameboard JSON portion of front end updates
    Ignores any client->server comms [client socket send()] on this socket
    """

    def connect(self):
        self.user = self.scope["user"]
        self.game_name = self.scope['url_route']['kwargs']['game_name']
        user_has_game_auth = GameModelInterface.user_is_authenticated_to_game(
            self.user, self.game_name)
        if self.user.is_authenticated and user_has_game_auth:
            authlog.info('User {} connected gameboard socket for game {}'.format(
                self.user.username, self.game_name))
            generallog.info('Subscribing user {} gameboard socket to game {} group'.format(
                self.user.username, self.game_name))
            async_to_sync(self.channel_layer.group_add)(
                self.game_name, self.channel_name)
            self.accept()
            GameModelInterface.create_or_rejoin_game(self.user, self.game_name)
            generallog.info('Updating lobby')
            update_game_lobby(self.channel_layer)
            frontend_update = GameModelInterface.get_current_game_state(
                self.user, self.game_name)
            if frontend_update is not None:
                update_gameboard(self.channel_layer,
                                 self.game_name, frontend_update)
        else:
            authlog.warning('Unauthorized user {} attempted to connect a socket to game {}'.format(
                self.user.username, self.game_name))
            return  # User isn't authenticated OR not authenticated to game

    def disconnect(self, close_code):
        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_discard)(
                self.game_name, self.channel_name)

    def receive(self, text_data):
        """Ignore any client->server comms for this socket"""
        return

    def frontend_update(self, event):
        self.send(text_data=event["text"])


class UserGameRoomSocketConsumer(WebsocketConsumer):
    """
    Socket consumer for receiving user input and returning status
    Client->server [client socket send()] comms on this socket are for user input
    Client socket onRecieve() accepts and displays status portion of JSON e.g. "Player 2 turn"
    """

    def connect(self):
        self.user = self.scope["user"]
        self.game_name = self.scope['url_route']['kwargs']['game_name']
        user_has_game_auth = GameModelInterface.user_is_authenticated_to_game(
            self.user, self.game_name)
        if self.user.is_authenticated and user_has_game_auth:
            authlog.info('User {} connected gameroom socket for game {}'.format(
                self.user.username, self.game_name))
            generallog.info('Subscribing user {} gameroom socket to game {} group'.format(
                self.user.username, self.game_name))
            async_to_sync(self.channel_layer.group_add)(
                self.game_name, self.channel_name)
            self.accept()
        else:
            authlog.warning('Unauthorized user {} attempted to connect a socket to game {}'.format(
                self.user.username, self.game_name))
            return  # User isn't authenticated OR not authenticated to game

    def disconnect(self, close_code):
        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_discard)(
                self.game_name, self.channel_name)

    # Reception of user input from user game room socket
    def receive(self, text_data):
        if self.user.is_authenticated:
            text_data_json = json.loads(text_data)
            game_name = text_data_json['game']
            move = text_data_json['move']
            backend_update = BackEndUpdate(self.user, game_name, move)
            frontend_update = GameModelInterface.give_update(backend_update)
            if frontend_update is not None:
                update_gameboard(self.channel_layer,
                                 self.game_name, frontend_update)

    def frontend_update(self, event):
        self.send(text_data=event["text"])


class UserGameLobbyConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            authlog.info('User {} connected to a lobby socket'.format(
                self.user.username))
            generallog.info('Subscribing user {} lobby socket to lobby group'.format(
                self.user.username))
            async_to_sync(self.channel_layer.group_add)(
                'lobby', self.channel_name)
            self.accept()
            self.send(json.dumps(GameModelInterface.get_lobby_games()))
        else:
            authlog.warning('Unauthorized user {} attempted to connect a socket to lobby'.format(
                self.user.username, self.game_name))

    def disconnect(self, close_code):
        if self.user.is_authenticated:
            # Remove from lobby group
            async_to_sync(self.channel_layer.group_discard)(
                'lobby', self.channel_name)

    def receive(self, text_data):
        """Ignore any client->server comms for this socket"""
        return

    def lobby_update(self, event):
        self.send(text_data=event["text"])
