import json
from channels.generic.websocket import WebsocketConsumer
from game.interfaces import BackEndUpdate
from game.interfaces import GameModelInterface
from asgiref.sync import async_to_sync


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
            async_to_sync(self.channel_layer.group_add)(
                self.game_name, self.channel_name)
            self.accept()
            GameModelInterface.create_or_rejoin_game(self.user, self.game_name)
            frontend_update = GameModelInterface.get_current_game_state(
                self.user, self.game_name)
            async_to_sync(self.channel_layer.group_send)(
                self.game_name,
                {
                    "type": "front_end_update",
                    "text": frontend_update.serialize(),
                },
            )
        else:
            return  # User isn't authenticated OR not authenticated to game

    def disconnect(self, close_code):
        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_discard)(
                self.game_name, self.channel_name)

    def receive(self, text_data):
        """Ignore any client->server comms for this socket"""
        return

    def front_end_update(self, event):
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
            async_to_sync(self.channel_layer.group_add)(
                self.game_name, self.channel_name)
            self.accept()
        else:
            return  # User isn't authenticated OR not authenticated to game

    def disconnect(self, close_code):
        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_discard)(
                self.game_name, self.channel_name)

    # Reception of user input from user game room socket
    def receive(self, text_data):
        if self.user.is_authenticated:
            text_data_json = json.loads(text_data)
            game = text_data_json['game']
            move = text_data_json['move']
            backend_update = BackEndUpdate(self.user.username, game, move)
            frontend_update = GameModelInterface.give_update(backend_update)

            async_to_sync(self.channel_layer.group_send)(
                self.game_name,
                {
                    "type": "front_end_update",
                    "text": frontend_update.serialize(),
                },
            )

    def front_end_update(self, event):
        self.send(text_data=event["text"])


class UserGameLobbyConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_add)(
                'lobby', self.channel_name)
            self.accept()
            self.send(json.dumps(GameModelInterface.get_lobby_games()))

    def disconnect(self, close_code):
        if self.user.is_authenticated:
            # Remove from lobby group
            async_to_sync(self.channel_layer.group_discard)(
                'lobby', self.channel_name)

    def receive(self, text_data):
        """Ignore any client->server comms for this socket"""
        return
