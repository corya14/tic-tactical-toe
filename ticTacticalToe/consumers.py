import json
from channels.generic.websocket import WebsocketConsumer
from game.models import MockGame
#from channels.generic.websocket import JsonWebsocketConsumer
#from channels.generic.websocket import AsyncWebsocketConsumer

class UserSocketConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send( json.dumps( MockGame.gen_initial_game_dict() ) )

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        game_dict = MockGame.gen_dummy_dict()

        self.send( text_data=json.dumps( game_dict ) )

        # self.send(text_data=json.dumps({
        #     'message': message
        # }))
