from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db import models
from game.models import Game

# Create your views here.


def statspage(request, username):
    if request.user.is_authenticated:

        # check if user exists
        if User.objects.filter(username=username).exists():
            user = User.objects.filter(username=username).get()
        else:
            user = request.user

        wins = 0
        losses = 0
        for game in Game.objects.filter(models.Q(creator=user) | models.Q(opponent=user)):
            if game.is_complete():
                if game.winner == user:
                    wins += 1
                else:
                    losses += 1
            else:
                # Count any unfinished game where it's user's turn as loss
                # Don't count game if no one ever joined
                if game.current_turn == user and game.opponent != None:
                    losses += 1

        return render(request, 'stats/statspage.html', {
            'username': user.username,
            'wins': wins,
            'losses': losses
        })
    else:
        return redirect('home')
