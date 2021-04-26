from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint

# Create your models here.


class Game(models.Model):
    game_name = models.CharField(max_length=100, unique=True)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='winner', null=True, blank=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='creator')
    opponent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='opponent', null=True, blank=True)
    current_turn = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='current_turn')

    # dates
    completed = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return 'Game #{0}'.format(self.pk)

    @staticmethod
    def get_available_games():
        return Game.objects.filter(opponent=None, completed=None)

    @staticmethod
    def exists(name):
        return Game.objects.filter(game_name=name).count() > 0

    @staticmethod
    def user_may_join_or_play_game(username, game_name):
        if not Game.exists(game_name):
            # Game DNE, user may create
            return True
        else:
            game = Game.objects.filter(game_name=game_name).get()
            if game.opponent is None:
                return True
            elif game.opponent.username == username:
                return True
            elif game.creator.username == username:
                return True
            else:
                return False

    @staticmethod
    def user_join_game(user, game_name):
        game = Game.objects.filter(game_name=game_name)
        if not game.creator.username == user.username:
            game.opponent = user
        else:
            pass  # creator may be rejoining

    @staticmethod
    def created_count(user):
        return Game.objects.filter(creator=user).count()

    @staticmethod
    def get_games_for_player(user):
        from django.db.models import Q
        return Game.objects.filter(Q(opponent=user) | Q(creator=user))

    @staticmethod
    def get_by_id(id):
        try:
            return Game.objects.get(pk=id)
        except Game.DoesNotExist:
            # TODO: Handle this exception
            pass

    @staticmethod
    def create_new(user, game_name):
        """
        Create a new game and game squares
        :param user: the user that created the game
        :return: a new game object
        """
        # make the game's name from the username and the number of
        # games they've created
        new_game = Game(creator=user, current_turn=user, game_name=game_name)
        new_game.save()
        # for each row, create the proper number of GameSquares based on rows
        for row in range(1, 6):
            for col in range(1, 6):
                new_square = GameSquare(
                    game=new_game,
                    row=row,
                    col=col
                )
                new_square.save()
        new_game.get_game_square(1, 3).set_tacs(2)
        new_game.get_game_square(5, 3).claim(user, 1)
        # put first log into the GameLog
        new_game.add_log('Game created by {0}'.format(
            new_game.creator.username))

        return new_game

    def add_log(self, text, user=None):
        """
        Adds a text log associated with this game.
        """
        entry = GameLog(game=self, text=text, player=user).save()
        return entry

    def get_all_game_squares(self):
        """
        Gets all of the squares for this Game
        """
        return GameSquare.objects.filter(game=self)

    def get_game_square(self, row, col):
        """
        Gets a square for a game by it's row and col pos
        """
        try:
            return GameSquare.objects.get(game=self, col=col, row=row)
        except GameSquare.DoesNotExist:
            return None

    def get_square_by_coords(self, coords):
        """
        Retrieves the GameSquare based on it's (x,y) or (row, col)
        """
        try:
            square = GameSquare.objects.get(row=coords[1],
                                            col=coords[0],
                                            game=self)
            return square
        except GameSquare.DoesNotExist:
            # TODO: Handle exception for gamesquare
            return None

    def get_game_log(self):
        """
        Gets the entire log for the game
        """
        return GameLog.objects.filter(game=self)

    def send_game_update(self):
        """
        Send the updated game information and squares to the game's channel group
        """
        # imported here to avoid circular import
        from .serializers import GameSquareSerializer, GameLogSerializer, GameSerializer

        squares = self.get_all_game_squares()
        square_serializer = GameSquareSerializer(squares, many=True)

        # get game log
        log = self.get_game_log()
        log_serializer = GameLogSerializer(log, many=True)

        game_serilizer = GameSerializer(self)

        message = {'game': game_serilizer.data,
                   'log': log_serializer.data,
                   'squares': square_serializer.data}

        game_group = 'game-{0}'.format(self.id)
        Group(game_group).send({'text': json.dumps(message)})

    def next_player_turn(self):
        """
        Sets the next player's turn
        """
        self.current_turn = self.creator if self.current_turn != self.creator else self.opponent
        self.save()

    def mark_complete(self, winner):
        """
        Sets a game to completed status and records the winner
        """
        self.winner = winner
        self.completed = datetime.now()
        self.save()


class GameSquare(models.Model):

    class Meta:
        constraints = [
            models.UniqueConstraint(name='uniqueness', fields=[
                                    'game', 'row', 'col'])
        ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    tacs = models.IntegerField(default=0)
    row = models.IntegerField()
    col = models.IntegerField()

    # dates
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '{0} - ({1}, {2})[{3}]'.format(self.game, self.col, self.row, self.tacs)

    @staticmethod
    def get(row, col, game):
        return GameSquare.objects.filter(row=row, col=col, game=game).get()

    def set_tacs(self, tacs):
        self.tacs = tacs
        self.save(update_fields=['tacs'])

    @staticmethod
    def get_by_id(id):
        try:
            return GameSquare.objects.get(pk=id)
        except GameSquare.DoesNotExist:
            # TODO: Handle exception for gamesquare
            return None

    def claim(self, user, tacs):
        """
        Claims the square for the user
        """
        self.owner = user
        self.tacs = tacs
        self.save(update_fields=['owner', 'tacs'])

        # add log entry for move
        self.game.add_log('GameSquare ({0}, {1}) claimed with {2} tacs by {3}'
                          .format(self.col, self.row, self.tacs, self.owner.username))


class GameLog(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return 'Game #{0} Log'.format(self.game.id)
