import json
from channels.generic.websocket import WebsocketConsumer
from game.models import MockGame
from asgiref.sync import async_to_sync
#from channels.generic.websocket import JsonWebsocketConsumer
#from channels.generic.websocket import AsyncWebsocketConsumer

class UserSocketConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_add)(self.user.username, self.channel_name)
            self.accept()
            self.send( json.dumps( MockGame.gen_initial_game_dict() ) )

    def disconnect(self, close_code):
        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_discard)(self.user.username, self.channel_name)

    def receive(self, text_data):
        if self.user.is_authenticated:
            text_data_json = json.loads(text_data)
            message = "USER[{}]GAME[{}]MOVE[{}]".format(self.user.username, text_data_json['game'], text_data_json['move'])
            print(message)

            game_dict = MockGame.gen_dummy_dict()

            async_to_sync(self.channel_layer.group_send)(
                self.user.username,
                {
                    "type": "gameboard_update",
                    "text": json.dumps( game_dict ),
                },
            )

    def gameboard_update(self, event):
        self.send( text_data=event["text"] )
