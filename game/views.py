from django.shortcuts import render, redirect
from game.interfaces import GameModelInterface
from django.contrib import messages

# Create your views here.


def lobby(request):
    if request.user.is_authenticated:
        return render(request, 'game/lobby.html', {
            'requesting_user': request.user.username
        })


def gameroom(request, game_name):
    if request.user.is_authenticated:
        if GameModelInterface.user_is_authenticated_to_game(request.user, game_name):
            return render(request, 'game/gameroom.html', {
                'game_name': game_name,
                'requesting_user': request.user.username
            })
        else:
            messages.error(request, "Invalid game name. Please try again.")
            return redirect('lobby')
