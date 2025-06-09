from django.contrib import admin
from .models import Game, Player, Referee, Round, Tournament
from django.contrib.auth.models import User

admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Referee)
admin.site.register(Round)
admin.site.register(Tournament)