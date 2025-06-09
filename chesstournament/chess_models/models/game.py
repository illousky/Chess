from django.db import models
from chess_models.models.constants import Scores
import requests
from chess_models.models.player import LichessAPIError
from chess_models.models.round import Round


class Game(models.Model):

    white = models.ForeignKey('Player',
                              on_delete=models.CASCADE,
                              related_name='white_player',
                              null=True, blank=True)
    black = models.ForeignKey('Player',
                              on_delete=models.CASCADE,
                              related_name='black_player',
                              null=True, blank=True)
    finished = models.BooleanField(default=False)
    round = models.ForeignKey('Round', on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    result = models.CharField(max_length=1, default=Scores.NOAVAILABLE)
    rankingOrder = models.IntegerField(default=0)

    def __str__(self):

        white_name = str(self.white)
        black_name = str(self.black)
        result_label = Scores(self.result).label

        return f"{white_name}({self.white.id})" + \
            f" vs {black_name}({self.black.id}) = {result_label}"

    def get_lichess_game_result(self, game_id):

        url = f"https://lichess.org/api/game/{game_id}"
        response = requests.get(url)

        if response.status_code == 200:

            data = response.json()

            try:
                white_player = data["players"]["white"]["userId"]
                black_player = data["players"]["black"]["userId"]
                if white_player is None:
                    white_player_lower = None
                else:
                    white_player_lower = white_player.lower()
                if black_player is None:
                    black_player_lower = None
                else:
                    black_player_lower = black_player.lower()
            except Exception:
                return (Scores.NOAVAILABLE.value, None, None)

            if self.white is None:
                my_white_player = None
            else:
                my_white_player = str(self.white).lower()

            if self.black is None:
                my_black_player = None
            else:
                my_black_player = str(self.black).lower()

            if my_white_player != white_player_lower \
               or my_black_player != black_player_lower:
                raise LichessAPIError(
                    f"Players for game {game_id} are different"
                )

            try:
                winner = data["winner"]

                if winner == "black":
                    result = Scores.BLACK.value
                elif winner == "white":
                    result = Scores.WHITE.value
            except Exception:
                result = Scores.DRAW.value

        else:
            raise LichessAPIError("Failed to fetch data for game {game_id}")

        return (result, white_player, black_player)


def create_rounds(tournament, swissByes=[]):

    # Extraemos lista de jugadores
    players = list(tournament.getPlayers())
    number_of_players = len(players)
    rounds = []

    # Si el numero de jugadores es impar, añadir jugador invisible
    if number_of_players % 2 != 0:
        players.append(None)
        number_of_players += 1

    number_of_rounds = number_of_players - 1  # Calcular numero de rondas
    rotate = (number_of_players/2) - 1

    for i in range(number_of_rounds):  # Para cada ronda

        round = []

        # Para cada partida de la ronda
        for j in range(number_of_players//2):

            p1 = players[j]
            p2 = players[number_of_players - 1 - j]

            if p2 != players[number_of_players - 1]:
                round.append([p1, p2])
            elif j == 0 and i % 2 == 0:
                round.append([p1, p2])
            else:
                round.append([p2, p1])

        rounds.append(round)  # Añadir ronda a la lista de rondas

        # El ultimo jugador de la lista se mantiene fijo
        last_player = players.pop()

        # Alterar la lista de jugadores para la siguiente ronda
        for i in range(int(rotate)):
            players.insert(0, players.pop())

        players.append(last_player)

    for round in rounds:

        created_round = Round.objects.create(
            tournament=tournament,
            name="Round_" + str(rounds.index(round) + 1)
        )

        for game in round:

            if game[0] is not None and game[1] is not None:

                Game.objects.create(white=game[0],
                                    black=game[1],
                                    round=created_round)

    return rounds  # Devolver lista de rondas
