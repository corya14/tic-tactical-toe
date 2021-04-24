# Encapculates an update to the back end
class BackEndUpdate():
   def __init__(self, user, game, move):
      self._user = user
      self._game = game
      self._move = move
   def user(self):
      return self._user
   def game(self):
      return self._game
   def move(self):
      return self._move
   def __str__(self):
      return "BackEndUpdate{{USER[{}]GAME[{}]MOVE[{}]}}".format(self._user, self._game, self._move)

# Encapsulates an update to the front end
class FrontEndUpdate():

   @staticmethod
   def square_dict( id, color='white', value=0 ):
      """Maintain as dict for easy serialization"""
      d = {}
      d['id'] = id
      d['color'] = color
      d['value'] = value
      return d

   def __init__(self):
      self.game_dict = {}
      self.game_dict["gameboard"] = {}
      self.gameboard = game_dict["gameboard"]
      self.game_dict["status"] = ""
      self.status = game_dict["status"]
      self.game_dict["log"] = []
      self.gamelog = game_dict["log"]
      rows = [1, 2, 3, 4, 5]
      cols = ['a', 'b', 'c', 'd', 'e']
      for row in rows:
         for col in cols:
            self.init_square(row, col)
      return game_dict

   @staticmethod
   def get_square_id( row, col ):
      return str(row) + str(col)

   def init_square( self, row, col ):
      id = FrontEndUpdate.get_square_id( row, col )
      self.gameboard[id] = FrontEndUpdate.square_dict(id)

   def set_square(self, row, col, square):
      self.game_dict["gameboard"][FrontEndUpdate.get_square_id(row,col)] = square


# Define an object adapter for interactions with game model
class GameModelInterface():
   @staticmethod
   def user_is_authenticated_to_game( user, game_name ) -> bool:
      """Return true if user is auth'd to game, or game needs a new player"""
      # FIXME
      return True

   @staticmethod
   def give_update( backend_update ) -> FrontEndUpdate:
      """
      Accept move_str from user for given game (str name of game)
      Should check:
         Is the user auth'd to this game?
         Is it the users turn?
         Is the move valid?
      Then:
         Update the state of the game
         Change active turn
      Finally:
         yield FrontEndUpdate with applicable status
      """
      print( str(backend_update) )

   @staticmethod
   def get_lobby_games():
      """ Return list of games that need another player """
      #TODO: Replace with model query for games in need of another player
      return [ "game1", "game2", "game3" ]
