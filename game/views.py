from django.shortcuts import render

# Create your views here.

def lobby(request):
    return render(request, 'game/lobby.html')

def gameroom(request, room_name):
    return render(request, 'game/gameroom.html', {
        'room_name': room_name
    })
