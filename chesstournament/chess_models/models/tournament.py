from django.db import models
from django.contrib.auth.models import User
from chess_models.models.constants import RankingSystem
from chess_models.models.game import Game
from chess_models.models.round import Round
from chess_models.models.constants import Scores


class Tournament(models.Model):

    name = models.CharField(max_length=128, unique=True, blank=True, null=True)
    administrativeUser = models.ForeignKey(User,
                                           on_delete=models.CASCADE,
                                           null=True)
    players = models.ManyToManyField('Player', through='FechaApuntadoATorneo',
                                     blank=True)
    referee = models.ForeignKey('Referee', on_delete=models.CASCADE, null=True,
                                default=None)
    start_date = models.DateTimeField(auto_now=True, null=True)
    end_date = models.DateTimeField(null=True, default=None)
    max_update_time = models.IntegerField(default=43200)
    only_administrative = models.BooleanField(default=False)
    tournament_type = models.CharField(max_length=2)
    tournament_speed = models.CharField(max_length=2)
    board_type = models.CharField(max_length=3)
    win_points = models.FloatField(default=1.0)
    draw_points = models.FloatField(default=0.5)
    lose_points = models.FloatField(default=0.0)
    timeControl = models.CharField(max_length=32, default='15+0')
    number_of_rounds_for_swiss = models.IntegerField(default=0)
    rankingList = models.ManyToManyField('RankingSystemClass', blank=True)

    def getPlayers(self, sorted=False):
        
        if sorted:
            
            if self.board_type == 'LIC':
                if self.tournament_speed == 'BU':
                    return self.players.order_by('lichess_rating_bullet')
                elif self.tournament_speed == 'BL':
                    return self.players.order_by('lichess_rating_blitz')
                elif self.tournament_speed == 'RA':
                    return self.players.order_by('lichess_rating_rapid')
                elif self.tournament_speed == 'CL':
                    return self.players.order_by('lichess_rating_classical')
            else:
                if self.tournament_speed == 'BL':
                    return self.players.order_by('fide_rating_blitz')
                elif self.tournament_speed == 'RA':
                    return self.players.order_by('fide_rating_rapid')
                elif self.tournament_speed == 'CL':
                    return self.players.order_by('fide_rating_classical')
        
        
        return self.players.all()

    def getPlayersCount(self):
        return self.players.count()

    def __str__(self):
        return self.name

    def getRankingList(self):
        return self.rankingList.all()

    def cleanRankingList(self):
        self.rankingList.clear()

    def addToRankingList(self, rankingSystem):
        ranking_system, created = \
            RankingSystemClass.objects.get_or_create(value=rankingSystem)
        self.rankingList.add(ranking_system)

    def removeFromRankingList(self, rankingSystem):
        rankingSystem = RankingSystemClass.objects.get(value=rankingSystem)
        self.rankingList.remove(rankingSystem)

    def getRoundCount(self):
        return Round.objects.filter(tournament=self).count()

    def get_number_of_rounds_with_games(self):

        rounds = Round.objects.filter(tournament=self)

        i = 0

        for round in rounds:
            if Game.objects.filter(round=round).count() > 0:
                i += 1

        return i

    def get_latest_round_with_games(self):

        rounds = Round.objects.filter(tournament=self)
        rounds = rounds.order_by('-start_date')

        for round in rounds:
            if Game.objects.filter(round=round).count() > 0:
                return round

        return None

    def getGames(self):
        return Game.objects.filter(round__tournament=self)


class FechaApuntadoATorneo(models.Model):

    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


class RankingSystemClass(models.Model):

    value = models.CharField(
        max_length=2,
        choices=RankingSystem.choices,
        primary_key=True
    )


def getScores(tournament):

    PLAIN_SCORE = RankingSystem.PLAIN_SCORE.value

    results = {}
    players = tournament.getPlayers()

    for player in players:
        results[player] = {}
        results[player][PLAIN_SCORE] = 0

    rounds = Round.objects.filter(tournament=tournament)

    for round in rounds:

        games = Game.objects.filter(round=round, finished=True)

        for game in games:

            if game.white is None and game.black is None:
                continue

            try:
                if game.result == Scores.WHITE:
                    results[game.white][PLAIN_SCORE] += tournament.win_points
                    results[game.black][PLAIN_SCORE] += tournament.lose_points
                elif game.result == Scores.BLACK:
                    results[game.white][PLAIN_SCORE] += tournament.lose_points
                    results[game.black][PLAIN_SCORE] += tournament.win_points
                elif game.result == Scores.DRAW:
                    results[game.white][PLAIN_SCORE] += tournament.draw_points
                    results[game.black][PLAIN_SCORE] += tournament.draw_points
                elif game.result == Scores.FORFEITWIN:
                    results[game.white][PLAIN_SCORE] += tournament.win_points
                elif game.result == Scores.BYE_H:
                    results[game.white][PLAIN_SCORE] += tournament.draw_points
                elif game.result == Scores.BYE_F:
                    results[game.white][PLAIN_SCORE] += tournament.win_points
                elif game.result == Scores.BYE_U:
                    results[game.white][PLAIN_SCORE] += tournament.win_points
            except Exception as e:
                print(e.strerror)

    return results


def getBlackWins(tournament, results):
    WINS = RankingSystem.WINS.value
    BLACKTIMES = RankingSystem.BLACKTIMES.value

    players = tournament.getPlayers()

    for player in players:
        results[player][WINS] = 0
        results[player][BLACKTIMES] = 0

    rounds = Round.objects.filter(tournament=tournament)

    for round in rounds:

        games = Game.objects.filter(round=round, finished=True)

        for game in games:

            if game.white is None and game.black is None:
                continue

            if game.black is not None:
                if game.result == Scores.WHITE or \
                    game.result == Scores.BLACK or \
                        game.result == Scores.DRAW:
                    results[game.black][BLACKTIMES] += 1

            if game.result == Scores.WHITE:
                results[game.white][WINS] += 1

            elif game.result == Scores.BLACK:
                results[game.black][WINS] += 1

    return results


def getRanking(tournament):
    
    RANK = "rank"
    PLAIN_SCORE = RankingSystem.PLAIN_SCORE.value

    rounds = Round.objects.filter(tournament=tournament)

    partida_jugada = False
    
    for round in rounds:
        games = Game.objects.filter(round=round, finished=True)

        if games.count() > 0:
            partida_jugada = True
    
    if partida_jugada is False:
        
        # convert a queryset to dict
        # and add the rank to each player
        results = {}
        players = tournament.getPlayers()
        
        for i, player in enumerate(list(players)):
            results[player] = {}
            results[player][RANK] = i+1
            results[player][PLAIN_SCORE] = 0
        
        return results
        
    results = getScores(tournament)
    results = getBlackWins(tournament, results)
    
    # ordena por score, en caso de empate por wins
    # y en caso de empate por blacktimes
    sorted_results = sorted(
                    results.items(),
                    key=lambda x:
                    (x[1][PLAIN_SCORE],
                        x[1].get(RankingSystem.WINS, 0),
                        x[1].get(RankingSystem.BLACKTIMES, 0)),
                    reverse=True)

    rank = 1
    for player, score in sorted_results:
        results[player][RANK] = rank
        rank += 1

    return results
