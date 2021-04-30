import json
from game.models import Game
from game.models import GameSquare

import logging
gameslog = logging.getLogger('games')

cols = {}
cols['a'] = 1
cols['b'] = 2
cols['c'] = 3
cols['d'] = 4
cols['e'] = 5


class BackEndUpdate():
    """Encapculates an update to the back end
    """

    def __init__(self, user, game_name, move):
        self._user = user
        self._game_name = game_name
        self._move = move
        self._src_sq = self._set_src_square()
        self._dst_sq = self._set_dst_square()
        self._num_tacs = self._set_num_tacs()

    def user(self):
        return self._user

    def game_name(self):
        return self._game_name

    def move(self):
        return self._move

    def src(self):
        return self._src_sq

    def dst(self):
        return self._dst_sq

    def tacs(self):
        return self._num_tacs

    def _set_src_square(self):
        game = Game.objects.filter(game_name=self._game_name).get()
        # (1)(a1,a1)
        #     ^^
        src_str = self._move.split('|')[1][1:3]
        col = cols[src_str[0]]
        row = src_str[1]
        return game.get_game_square(row, col)

    def _set_dst_square(self):
        game = Game.objects.filter(game_name=self._game_name).get()
        # (1)(a1,a1)
        #        ^^
        dst_str = self._move.split('|')[1][4:6]
        col = cols[dst_str[0]]
        row = dst_str[1]
        return game.get_game_square(row, col)

    def _set_num_tacs(self):
        return int(self._move.split('|')[0].replace('(', '').replace(')', ''))

    def __str__(self):
        return "BackEndUpdate{{USER[{}]GAME[{}]MOVE[{}]}}".format(self._user, self._game_name, self._move)


class FrontEndUpdate():
    """ Encapsulates an update to the front end
    """

    @staticmethod
    def square_dict(id, color='white', value=0):
        """Maintain as dict for easy serialization"""
        d = {}
        d['id'] = id
        d['color'] = color
        d['value'] = value
        return d

    def __init__(self):
        self.data_dict = {}
        self.data_dict["player1"] = ''
        self.data_dict["player2"] = ''
        self.data_dict["current_turn"] = 'player1'
        self.data_dict["gameboard"] = {}
        self.gameboard = self.data_dict["gameboard"]
        self.data_dict["status"] = ""
        self.status = self.data_dict["status"]
        self.data_dict["log"] = []
        self.gamelog = self.data_dict["log"]
        rows = [1, 2, 3, 4, 5]
        cols = ['a', 'b', 'c', 'd', 'e']
        for row in rows:
            for col in cols:
                self.init_square(row, col)
        self.set_square(1, 'c', 'red', 2)
        self.set_square(5, 'c', 'cyan', 1)

    @staticmethod
    def get_square_id(row, col):
        return str(row) + str(col)

    @staticmethod
    def int_col_to_char(col):
        if col == 1:
            return 'a'
        elif col == 2:
            return 'b'
        elif col == 3:
            return 'c'
        elif col == 4:
            return 'd'
        elif col == 5:
            return 'e'
        else:
            return None

    def set_status(self, status):
        self.status = status

    def set_player1(self, player1):
        self.data_dict["player1"] = player1

    def set_player2(self, player2):
        self.data_dict["player2"] = player2

    def set_current_turn_creator(self):
        self.data_dict["current_turn"] = 'player1'

    def set_current_turn_opponent(self):
        self.data_dict["current_turn"] = 'player2'

    def init_square(self, row, col):
        id = FrontEndUpdate.get_square_id(row, col)
        self.gameboard[id] = FrontEndUpdate.square_dict(id)

    def get_square(self, row, col):
        return self.gameboard[self.get_square_id(row, col)]

    def set_square(self, row, col, color, value):
        self.get_square(row, col)['color'] = color
        self.get_square(row, col)['value'] = value

    def make_square_blue(self, row, col):
        self.get_square(row, col)['color'] = 'cyan'

    def make_square_red(self, row, col):
        self.get_square(row, col)['color'] = 'red'

    def set_square_value(self, row, col, value):
        self.get_square(row, col)['value'] = value

    def serialize(self):
        return json.dumps(self.data_dict)

# Define an object adapter for interactions with game model


class GameModelInterface():
    @staticmethod
    def user_is_authenticated_to_game(user, game_name) -> bool:
        """Return true if user is auth'd to game, or game needs a new player"""
        return Game.user_may_join_or_play_game(user, game_name)

    @staticmethod
    def create_or_rejoin_game(user, game_name):
        """Create a game if it doesn't exist and join"""
        if Game.exists(game_name):
            Game.user_join_game(user, game_name)
        else:
            Game.create_new(user, game_name)

    @staticmethod
    def game_to_frontend_update(game) -> FrontEndUpdate:
        return game.to_frontend_update()

    @staticmethod
    def get_current_game_state(user, game_name) -> FrontEndUpdate:
        game = Game.objects.filter(game_name=game_name)
        return GameModelInterface.game_to_frontend_update(game.get())

    @staticmethod
    def give_update(backend_update) -> FrontEndUpdate:
        # Some basic top level checks before update even gets to game
        try:
            game = Game.objects.filter(
                game_name=backend_update.game_name()).get()
        except:
            gameslog.warning(
                'Problem finding game {}'.format(backend_update.game_name()))
            return
        if not game.is_associated_with_user(backend_update.user()):
            gameslog.warning('Game {} is not associated with user {}'.format(
                backend_update.game_name(), backend_update.user().username))
            return
        elif not game.is_ready_to_play():
            gameslog.warning(
                'Game {} is not ready to play'.format(backend_update.game_name()))
            return
        else:
            # User is part of game and game is ready to play
            gameslog.info('Received update for game {}'.format(
                backend_update.game_name()))
            frontend_update = game.update(backend_update)
            return frontend_update

    @staticmethod
    def get_lobby_games():
        """ Return list of games that need another player """
        avail_games = Game.get_available_games()
        avail_games_list = [x.game_name for x in avail_games]
        return avail_games_list
