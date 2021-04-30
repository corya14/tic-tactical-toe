from django.shortcuts import render, redirect
from game.interfaces import GameModelInterface
from django.contrib import messages
import re
import logging

authlog = logging.getLogger('auth')

VERIFY_REGEX = re.compile(r'^[a-zA-Z0-9_]+$')

# Create your views here.


def lobby(request):
    if request.user.is_authenticated:
        return render(request, 'game/lobby.html', {
            'requesting_user': request.user.username
        })


def gameroom(request, game_name):
    if request.user.is_authenticated:
        # test to see if game exists and is completed
        if GameModelInterface.is_game_complete(game_name):
            # Any user may see the final state of the game
            return render(request, 'game/gameroom.html', {
                'game_name': game_name,
                'requesting_user': request.user.username
            })

        if VERIFY_REGEX.match(game_name):
            if GameModelInterface.user_is_authenticated_to_game(request.user, game_name):
                return render(request, 'game/gameroom.html', {
                    'game_name': game_name,
                    'requesting_user': request.user.username
                })
            else:
                authlog.warning('User {} failed to authenticate to game {}'.format(
                    request.user.username, game_name))
                messages.error(request, "Not allowed to join that game. Please try again.")
                return redirect('lobby')
        else:
            authlog.debug('User {} tried to create a game with an invalid name.'.format(
                request.user.username))
            messages.error(request, "Invalid game name. Please try again.")
            return redirect('lobby')
