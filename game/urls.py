from django.urls import path
from . import views

urlpatterns = [
    path('lobby/', views.lobby, name='lobby'),
    path('<str:game_name>/', views.gameroom, name='gameroom'),
]
