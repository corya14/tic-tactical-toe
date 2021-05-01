from django.test import TestCase
from game.models import Game
from django.contrib.auth.models import User
from game.interfaces import BackEndUpdate

# Create your tests here.

class GameTestCase(TestCase):
    def setUp(self):
        user1 = User.objects.create(username='user1')
        user2 = User.objects.create(username='user2')
        game = Game.create_new(user1, 'game1')
        Game.user_join_game(user2,'game1')

    def test_attacking(self):
        # Let's force an attacking situation
        user1 = User.objects.get(username='user1')
        user2 = User.objects.get(username='user2')
        game = Game.objects.get(game_name='game1')
        src = game.get_game_square(3,3)
        dst = game.get_game_square(3,2)
        src.claim(user1,1)
        dst.claim(user2,2)
        while game.get_game_square(3,3).tacs > 0 and game.current_turn != user2:
            backend_update = BackEndUpdate(user1, 'game1', '(1)|(c3,b3)')
            frontend_update = game.update(backend_update)
            src = game.get_game_square(3,3)
            dst = game.get_game_square(3,2)
            print(src.tacs)
            print(src.owner.username)
            print(dst.tacs)
            print(dst.owner.username)

        if src.owner == dst.owner:
            # Attacker must have won, src should have 1 tacs now
            self.assertEqual(1,src.tacs)
            # And it should now be user2's turn
            game = Game.objects.get(game_name='game1')
            self.assertEqual(user2, game.current_turn)
        else:
            # Attacker must have lost
            self.assertEqual(0,src.tacs)
            # And it should still be user1's turn
            game = Game.objects.get(game_name='game1')
            self.assertEqual(user1, game.current_turn)
