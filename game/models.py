from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint
import re
import secrets
from datetime import datetime

import logging
gameslog = logging.getLogger('games')
authlog = logging.getLogger('auth')


# Move verification regex
VERIFY_REGEX = re.compile(r'^\([0-9]?\)|\([a-e][1-5],[a-e][1-5]\)$')

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
    def user_may_join_or_play_game(user, game_name):
        # Make sure user doesn't have a bunch of other unfinished games
        unfinished = Game.objects.filter(models.Q(completed=None) & (
            models.Q(creator=user) | models.Q(opponent=user)))
        if len(unfinished) >= 5:
            authlog.info(
                'Restricting user {} game creations. They have 5+ unfinished games.'.format(user.username))

        if not Game.exists(game_name):
            if len(unfinished) < 5:
                # Game DNE, user may create
                authlog.info(
                    'User {} may join game {} - Game is new'.format(user.username, game_name))
                return True
            else:
                authlog.warning(
                    'User {} may not create new game. They have 5+ unfinished games.'.format(user.username))
                return False
        else:  # game exists
            game = Game.objects.filter(game_name=game_name).get()
            if game.is_complete():
                authlog.info(
                    'User {} may view game {} - Game completed'.format(user.username, game_name))
                return True
            elif game.opponent is None:
                if len(unfinished) < 5:
                    authlog.info(
                        'User {} may join game {} - Game has no opponent yet'.format(user.username, game_name))
                    return True
                else:
                    authlog.warning(
                        'User {} may not join new game. They have 5+ unfinished games.'.format(user.username))
            elif game.opponent == user:
                authlog.info(
                    'User {} may join game {} - User is game opponent'.format(user.username, game_name))
                return True
            elif game.creator == user:
                authlog.info(
                    'User {} may join game {} - User is game creator'.format(user.username, game_name))
                return True
            else:
                authlog.info('User {} may not join game {}'.format(
                    user.username, game_name))
                return False

    @staticmethod
    def user_join_game(user, game_name):
        game = Game.objects.filter(game_name=game_name).get()
        if game.creator == user:
            authlog.info('Creator {} rejoining game {}'.format(
                user.username, game_name))
        elif game.opponent is None:
            game.opponent = user
            game.get_game_square(1, 3).claim(user, 2)
            game.save(update_fields=['opponent'])
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

    def is_ready_to_play(self):
        return self.creator != None and self.opponent != None

    def is_associated_with_user(self, user):
        return self.creator == user or self.opponent == user

    def is_valid_move(self, backend_update):

        if self.opponent is None or self.creator is None:
            gameslog.warning(
                "Invalid move: {} - Game {} isn't ready yet".format(backend_update.move(), backend_update.game_name()))
            return False

        if self.completed is not None:
            gameslog.warning(
                "Invalid move: {} - Game {} is completed".format(backend_update.move(), backend_update.game_name()))
            return False

        if not VERIFY_REGEX.match(backend_update.move()):
            gameslog.warning(
                'Invalid move: {} - Did not pass regex'.format(backend_update.move()))
            return False

        if not self.current_turn == backend_update.user():
            gameslog.warning(
                'Invalid move: {} - Out of turn'.format(backend_update.move()))
            return False

        src_sq = backend_update.src()

        # check if user owns source square
        if not src_sq.owner == backend_update.user():
            gameslog.warning(
                "Invalid move: {} - User doesn't own src square".format(backend_update.move()))
            return False

        # Make sure source square has tacs
        if not src_sq.tacs > 0:
            gameslog.warning(
                "Invalid move: {} - Source has no tacs".format(backend_update.move()))
            return False

        dst_sq = backend_update.dst()

        if src_sq == dst_sq:
            gameslog.debug("Ignoring tacs quantity constraints for IDLE move {} by user {}".format(
                backend_update.move(), backend_update.user().username))
        else:
            # Make sure player isn't trying to move too many tacs
            if src_sq.tacs < backend_update.tacs():
                gameslog.warning(
                    "Invalid move: {} - Source doesn't have enough tacs".format(backend_update.move()))
                return False

            # Avoid having more than 9 tacs in a square
            if dst_sq.owner == src_sq.owner and backend_update.tacs() + dst_sq.tacs > 9:
                gameslog.warning(
                    "Invalid move: {} - Destination would have too many tacs".format(backend_update.move()))
                return False

        # Make sure dst square is adjacent
        row_delta = abs(src_sq.row - dst_sq.row)
        col_delta = abs(src_sq.col - dst_sq.col)
        if row_delta + col_delta > 1:
            gameslog.warning(
                "Invalid move: {} - Dest not adjacent to source".format(backend_update.move()))
            return False

        return True

    def update(self, backend_update):
        if not self.is_valid_move(backend_update):
            gameslog.debug("User {} attempted invalid move {} in game {}".format(
                backend_update.user().username, backend_update.move(), backend_update.game_name()))
            frontend_update = self.to_frontend_update()
            frontend_update.set_status(
                'Invalid move: {}'.format(backend_update.move()))
            return frontend_update
        else:
            if self.process_valid_move(backend_update):
                self.finalize_turn()
            self.add_log('{}: {}'.format(backend_update.user(
            ).username, backend_update.move()), backend_update.user())
            return self.to_frontend_update()

    def process_valid_move(self, backend_update):
        src_sq = backend_update.src()
        dst_sq = backend_update.dst()
        tacs = backend_update.tacs()
        if dst_sq.owner == None:
            gameslog.debug('Processing invading move {}'.format(
                backend_update.move()))
            src_sq.delta_tacs(-1 * tacs)
            dst_sq.claim(backend_update.user(), tacs)
            return True
        elif src_sq == dst_sq:
            src_sq.set_tacs(min(9, src_sq.tacs + 2))
            return True
        elif dst_sq.owner == backend_update.user():
            gameslog.debug('Processing internal move {}'.format(
                backend_update.move()))
            src_sq.delta_tacs(-1 * tacs)
            dst_sq.delta_tacs(tacs)
            return True
        else:
            gameslog.debug('Processing conflict move {}'.format(
                backend_update.move()))
            attacking = tacs
            atk_loss = 0
            defending = dst_sq.tacs
            def_loss = 0
            gameslog.debug('{} attacking {} in game {}, {} vs {} tacs'.format(
                src_sq.owner.username, dst_sq.owner.username, backend_update.game_name(), attacking, defending))
            attacker_d6 = [x for x in range(0, min(3, attacking))]
            defender_d6 = [x for x in range(0, min(2, defending))]
            for i in range(0, len(attacker_d6)):
                attacker_d6[i] = secrets.randbelow(6) + 1
            for i in range(0, len(defender_d6)):
                defender_d6[i] = secrets.randbelow(6) + 1
            attacker_d6.sort(reverse=True)
            self.add_log('{} rolls: {}'.format(
                backend_update.user().username, attacker_d6), backend_update.user())
            gameslog.debug('Attacker rolls by {} in game {}: {}'.format(
                backend_update.user().username, backend_update.game_name(), attacker_d6))
            defender_d6.sort(reverse=True)
            self.add_log('{} rolls: {}'.format(
                dst_sq.owner.username, defender_d6), dst_sq.owner)
            gameslog.debug('Defender rolls by {} in game {}: {}'.format(
                dst_sq.owner.username, backend_update.game_name(), defender_d6))
            for i in range(0, len(defender_d6)):
                if attacker_d6[i] > defender_d6[i]:
                    defending -= 1
                    def_loss += 1
                    if defending == 0:
                        break
                else:
                    attacking -= 1
                    atk_loss += 1
            if defending == 0:
                dst_sq.claim(backend_update.user(), attacking)
                src_sq.delta_tacs(-1 * attacking)
                return True  # end turn
            else:
                src_sq.delta_tacs(-1 * atk_loss)
                dst_sq.delta_tacs(-1 * def_loss)
                return False

    def to_frontend_update(self):
        from game.interfaces import FrontEndUpdate
        frontend_update = FrontEndUpdate()
        if self.creator is not None:
            if self.current_turn == self.creator:
                frontend_update.set_current_turn_creator()
            frontend_update.set_player1(self.creator.username)
        if self.opponent is not None:
            if self.current_turn == self.opponent:
                frontend_update.set_current_turn_opponent()
            frontend_update.set_player2(self.opponent.username)
        for row in range(1, 6):
            for col in range(1, 6):
                char_col = FrontEndUpdate.int_col_to_char(col)
                gamesquare = GameSquare.objects.filter(
                    game=self, row=row, col=col).get()
                if gamesquare.owner == None:
                    color = 'white'
                elif gamesquare.owner == self.creator:
                    color = 'cyan'
                else:
                    color = 'red'
                frontend_update.set_square(
                    row=row, col=char_col, color=color, value=gamesquare.tacs)
        # Add game log
        for gamelog in self.get_game_log():
            frontend_update.add_log_entry(gamelog.text)
        return frontend_update

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

    def finalize_turn(self):
        """
        Sets the next player's turn
        """
        if self.get_game_square(1, 3).owner == self.creator:
            self.mark_complete(self.creator)
        elif self.get_game_square(5, 3).owner == self.opponent:
            self.mark_complete(self.opponent)
        else:
            for gamesquare in GameSquare.objects.filter(game=self, owner=self.current_turn):
                if gamesquare.tacs < 9:
                    gamesquare.delta_tacs(1)
            self.current_turn = self.creator if self.current_turn != self.creator else self.opponent
            self.save()

    def mark_complete(self, winner):
        """
        Sets a game to completed status and records the winner
        """
        self.winner = winner
        self.completed = datetime.now()
        self.add_log('{} wins!'.format(winner.username), winner)
        self.save()

    def is_complete(self):
        return self.completed != None


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

    @ staticmethod
    def get(row, col, game):
        return GameSquare.objects.filter(row=row, col=col, game=game).get()

    def set_tacs(self, tacs):
        self.tacs = tacs
        self.save(update_fields=['tacs'])

    def delta_tacs(self, delta):
        self.tacs += delta
        self.save(update_fields=['tacs'])

    @ staticmethod
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
        from game.interfaces import FrontEndUpdate
        self.owner = user
        self.tacs = tacs
        self.save(update_fields=['owner', 'tacs'])

        # add log entry for move
        self.game.add_log('GameSquare {0}{1} claimed with {2} tacs by {3}'
                          .format(FrontEndUpdate.int_col_to_char(self.col), self.row, self.tacs, self.owner.username))


class GameLog(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return 'Game #{0} Log'.format(self.game.id)
