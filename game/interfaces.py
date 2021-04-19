
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
      pass

   @staticmethod
   def give_move( user, game, move_str ) -> FrontEndUpdate:
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
      pass
