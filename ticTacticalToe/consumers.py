import json
from channels.generic.websocket import WebsocketConsumer
from game.models import Game
#from channels.generic.websocket import JsonWebsocketConsumer
#from channels.generic.websocket import AsyncWebsocketConsumer

cols = ['a', 'b', 'c', 'd', 'e']

def GridSquare( id, color='white', value=0 ):
    d = {}
    d['id'] = id
    d['color'] = color
    d['value'] = value
    return d

def get_base_game_dict():
    game_dict = {}
    game_dict["gameboard"] = {}

    for i in range(1,6):
        for col in cols:
            id = str(i) + col
            game_dict["gameboard"][id] = GridSquare( id )
    return game_dict

def gen_initial_game_dict():
    game_dict = get_base_game_dict()

    game_dict["gameboard"]["1c"]["color"]='red'
    game_dict["gameboard"]["1c"]["value"]=2
    game_dict["gameboard"]["5c"]["color"]='cyan'
    game_dict["gameboard"]["5c"]["value"]=1

    game_dict[ "status" ] = "Accepted"
    return game_dict

def gen_dummy_dict():
    game_dict = get_base_game_dict()

    game_dict["gameboard"]["1b"]["color"]='red'
    game_dict["gameboard"]["1b"]["value"]=1
    game_dict["gameboard"]["1c"]["color"]='red'
    game_dict["gameboard"]["1c"]["value"]=2
    game_dict["gameboard"]["1d"]["color"]='red'
    game_dict["gameboard"]["1d"]["value"]=3

    game_dict["gameboard"]["4c"]["color"]='cyan'
    game_dict["gameboard"]["4c"]["value"]=4
    game_dict["gameboard"]["5b"]["color"]='cyan'
    game_dict["gameboard"]["5b"]["value"]=3
    game_dict["gameboard"]["5c"]["color"]='cyan'
    game_dict["gameboard"]["5c"]["value"]=2
    game_dict["gameboard"]["5d"]["color"]='cyan'
    game_dict["gameboard"]["5d"]["value"]=1

    game_dict[ "status" ] = "Accepted"

    return game_dict

class UserSocketConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send( json.dumps( gen_initial_game_dict() ) )

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        game_dict = gen_dummy_dict()

        self.send( text_data=json.dumps( game_dict ) )

        # self.send(text_data=json.dumps({
        #     'message': message
        # }))
