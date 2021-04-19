from django.shortcuts import render
from game.interfaces import GameModelInterface

# Create your views here.

def lobby(request):
    return render(request, 'game/lobby.html')

def gameroom(request, game_name):
    if request.user.is_authenticated:
        if GameModelInterface.user_is_authenticated_to_game( request.user.username, game_name ):
            return render(request, 'game/gameroom.html', {
                'game_name': game_name,
                'requesting_user': request.user.username
            })
