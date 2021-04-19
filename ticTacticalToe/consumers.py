import json
from channels.generic.websocket import WebsocketConsumer
from game.models import MockGame
from game.interfaces import BackEndUpdate
from game.interfaces import GameModelInterface
from asgiref.sync import async_to_sync
#from channels.generic.websocket import JsonWebsocketConsumer
#from channels.generic.websocket import AsyncWebsocketConsumer

class UserSocketConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.game_name = self.scope['url_route']['kwargs']['game_name']
            async_to_sync(self.channel_layer.group_add)(self.game_name, self.channel_name)
            self.accept()
            self.send( json.dumps( MockGame.gen_initial_game_dict() ) )

    def disconnect(self, close_code):
        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_discard)(self.game_name, self.channel_name)

    def receive(self, text_data):
        if self.user.is_authenticated:
            text_data_json = json.loads(text_data)
            game = text_data_json['game']
            move = text_data_json['move']
            backend_update = BackEndUpdate( self.user.username, game, move )
            GameModelInterface.give_update( backend_update )

            game_dict = MockGame.gen_dummy_dict()

            async_to_sync(self.channel_layer.group_send)(
                self.game_name,
                {
                    "type": "gameboard_update",
                    "text": json.dumps( game_dict ),
                },
            )

    def gameboard_update(self, event):
        self.send( text_data=event["text"] )
