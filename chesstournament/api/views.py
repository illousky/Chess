from chess_models.models import (Referee, Player,
                                 Game, Tournament,
                                 Round, create_rounds,
                                 getRanking)
from rest_framework import viewsets
from chess_models.models.constants import Scores
from chess_models.models.player import LichessAPIError
from .serializers import (RefereeSerializer, PlayerSerializer,
                          GameSerializer, TournamentSerializer,
                          RoundSerializer, UserSerializer)
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from djoser.views import UserViewSet
from rest_framework.views import APIView
from rest_framework import permissions


class RefereeViewSet(viewsets.ModelViewSet):
    queryset = Referee.objects.all()
    serializer_class = RefereeSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class GameViewSet(viewsets.ModelViewSet):

    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'partial_update', 'update']:
            self.permission_classes = []

        return super().get_permissions()

    def update(self, request, *args, **kwargs):

        game_id = kwargs.get('pk')

        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"result": False,
                 "message": "Game does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        if game.finished and not request.user.is_authenticated:
            return Response(
                {"result": False,
                 "message":
                 "Authentication required to update a finished game."},
                status=status.HTTP_403_FORBIDDEN
            )

        result = request.data.get('result')
        game.result = result
        game.finished = True
        game.save()

        return Response(
            {"result": True, "message": "Game updated successfully."},
            status=status.HTTP_200_OK
        )


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class TournamentViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    queryset = Tournament.objects.all().order_by(
        '-start_date', '-id'
    )
    serializer_class = TournamentSerializer

    def get_permissions(self):

        if self.action in ['list', 'retrieve']:
            self.permission_classes = []

        return super().get_permissions()


class RoundViewSet(viewsets.ModelViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CreateRoundAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        if type(request.user) is type(User):
            return Response(
                {"result": False,
                 "message": "User is not admin"},
                status=status.HTTP_400_BAD_REQUEST
            )

        tournament_id = int(request.data.get('tournament_id'))

        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response(
                {"result": False,
                 "message": "Tournament not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if tournament.getPlayersCount() == 0:
            return Response(
                {"result": False,
                 "message": "No players in tournament"},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_rounds = create_rounds(tournament)

        if created_rounds:
            return Response(
                {"result": True},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"result": False,
                 "message": "Error creating rounds"},
                status=status.HTTP_400_BAD_REQUEST
            )


class SearchTournamentsAPIView(APIView):

    permission_classes = []

    def post(self, request):

        search_string = request.data.get('search_string')

        if not search_string:
            return Response(
                {"result": False,
                 "message": "search string is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        tournaments = Tournament.objects.filter(
            name__icontains=search_string
        ).order_by('-name')

        if not tournaments:
            return Response(
                {"result": False,
                 "message": "No tournaments found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        seralizer = TournamentSerializer(tournaments, many=True)

        return Response(
            seralizer.data,
            status=status.HTTP_200_OK
        )


class TournamentCreateAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        tournament_name = request.data.get('name')

        equal_tournaments = Tournament.objects.filter(name=tournament_name)

        if equal_tournaments:
            return Response(
                {"result": False,
                 "message": "Tournament already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        tournament_type = request.data.get('tournament_type')
        board_type = request.data.get('board_type')
        ranking_list = request.data.get('rankingList')
        players = request.data.get('players')

        tournament_speed = 'BU'
        only_administrative = False
        win_points = 1.0
        draw_points = 0.5
        lose_points = 0.0
        created_referee = None
        
        if request.data.get('tournament_speed'):
            tournament_speed = request.data.get('tournament_speed')

        if request.data.get('only_administrative'):
            only_administrative = request.data.get('only_administrative')

        if request.data.get('win_points'):
            win_points = request.data.get('win_points')

        if request.data.get('draw_points'):
            draw_points = request.data.get('draw_points')

        if request.data.get('lose_points'):
            lose_points = request.data.get('lose_points')

        if request.data.get('referee'):
            referee = request.data.get('referee')

            created_referee = Referee.objects.create(name=referee)

        player_list = players.split('\n')
        created_players = []

        if player_list[0] == "name, email":
            player_list = player_list[1:]

            for player in player_list:
                if player != '':
                    player_data = player.split(',')
                    player_create, created = Player.objects.get_or_create(
                        name=player_data[0],
                        email=player_data[1]
                    )
                    created_players.append(player_create)
        elif player_list[0] == "lichess_username":

            player_list = player_list[1:]
            for player in player_list:
                if player != '':
                    try:
                        player_create, created = Player.objects.get_or_create(
                            lichess_username=player
                        )

                        if str(player_create) == "invalid_lichess_user":
                            print("Lichess user not found")
                            return Response(
                                {"result": False,
                                "message": "User not found in lichess"},
                                status=status.HTTP_404_NOT_FOUND
                            )

                        created_players.append(player_create)
                    except Exception as ep:
                        print(ep)
        else:
            return Response(
                {"result": False,
                 "message": "Invalid players list"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            tournament = Tournament.objects.create(
                name=tournament_name,
                administrativeUser=request.user,
                only_administrative=only_administrative,
                tournament_type=tournament_type or "SR",
                board_type=board_type,
                win_points=win_points,
                draw_points=draw_points,
                lose_points=lose_points,
                tournament_speed=tournament_speed,
                referee=created_referee
            )
            tournament.players.set(created_players)
            tournament.rankingList.set(ranking_list)
        except Exception as e:
            print(e)
            return Response(
                {"result": False,
                 "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TournamentSerializer(tournament)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class GetRanking(APIView):

    permission_classes = []

    def get(self, request, tournament_id):

        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Exception:
            return Response(
                {"result": False,
                 "message": "Error: Tournament not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        ranking = getRanking(tournament)

        results = {}

        num_players = len(ranking.keys())

        for i in range(1, num_players + 1):
            results[str(i)] = {}

        for player in ranking.keys():

            i = ranking[player]['rank']
            results[str(i)]['id'] = player.id
            results[str(i)]['name'] = player.lichess_username if\
                player.lichess_username else player.name

            results[str(i)]['score'] = ranking[player]['PS']
            results[str(i)]['rank'] = ranking[player]['rank']

            if 'WI' in ranking[player]:
                results[str(i)]['WI'] = ranking[player]['WI']
            if 'BT' in ranking[player]:
                results[str(i)]['BT'] = ranking[player]['BT']

        return Response(
            results,
            status=status.HTTP_200_OK
        )


class GetPlayers(APIView):

    permission_classes = []

    def get(self, request, tournament_id):

        tournament = Tournament.objects.get(id=tournament_id)

        if not tournament:
            return Response(
                {"result": False,
                 "message": "Error: Tournament not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        players = tournament.getPlayers()
        players_serializer = PlayerSerializer(players, many=True)
        players_list = players_serializer.data

        return Response(
            players_list,
            status=status.HTTP_200_OK
        )


class GetRoundResults(APIView):

    permission_classes = []

    def get(self, request, tournament_id):

        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Exception:
            return Response(
                {"result": False,
                 "message": "Error: Tournament not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        rounds = Round.objects.filter(tournament=tournament).order_by('id')

        results = {}

        for i, round in enumerate(rounds):
            results[str(i)] = {}
            results[str(i)]['round_id'] = round.id
            results[str(i)]['round_name'] = round.name
            results[str(i)]['start_date'] = round.start_date

            games = Game.objects.filter(round=round).order_by('rankingOrder')

            results[str(i)]['games'] = {}

            for j, game in enumerate(games, 1):

                if game.white is None:
                    whiteId = 0
                    whiteName = None
                else:
                    whiteId = game.white.id
                    if game.white.lichess_username:
                        whiteName = game.white.lichess_username
                    else:
                        whiteName = game.white.name

                if game.black is None:
                    idBlack = 0
                    blackName = None
                else:
                    idBlack = game.black.id
                    if game.black.lichess_username:
                        blackName = game.black.lichess_username
                    else:
                        blackName = game.black.name

                results[str(i)]['games'][str(j)] = {
                    "id": game.id,
                    "rankingOrder": game.rankingOrder,
                    "white": whiteId,
                    "white_name": whiteName,
                    "black": idBlack,
                    "black_name": blackName,
                    "result": game.result,
                }

        return Response(
            results,
            status=status.HTTP_200_OK
        )


class UpdateLichessGameAPIView(APIView):

    permission_classes = []

    def post(self, request):

        game_id = request.data.get('game_id')
        lichess_game_id = request.data.get('lichess_game_id')

        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"result": False,
                 "message": "Game does not exist"})

        if game.finished is True:
            if not request.user.is_superuser:
                return Response(
                    {"result": False,
                     "message": "Game is blocked, only "
                     "administrator can update it"})

        try:
            winner, white, black = game.get_lichess_game_result(
                                        lichess_game_id)
        except LichessAPIError as e:
            return Response(
                {"result": False,
                 "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST)

        game.result = winner
        game.finished = True
        game.save()

        print(game)

        return Response(
            {"result": True},
            status=status.HTTP_200_OK
        )


class UpdateOTBGameAPIView(APIView):

    permission_classes = []

    def post(self, request):

        game_id = request.data.get('game_id')
        result = request.data.get('otb_result')

        if "email" not in request.data.keys():
            return Response(
                {"result": False,
                 "message": "Needed an email for update the game"})

        email = request.data.get('email')

        if result not in [
                            Scores.WHITE.value,
                            Scores.BLACK.value,
                            Scores.DRAW.value
                        ]:
            return Response(
                {"result": False,
                 "message": "Invalid result"})

        try:
            game = Game.objects.get(id=game_id)
        except Exception:
            return Response(
                {"result": False,
                 "message": "Game does not exist"})

        if game.finished is True:
            return Response(
                {"result": False,
                 "message": "Game is blocked, only "
                    "administrator can update it"})

        if email.strip() != game.white.email.strip() and email.strip() != game.black.email.strip():
            return Response(
                {"result": False,
                 "message": "Invalid email"})

        game.result = result
        game.finished = True
        game.save()

        return Response(
            {"result": True,
                "message": "Game updated by player"})


class AdminUpdateGameAPIView(APIView):

    permission_classes = []

    def post(self, request):

        game_id = request.data.get('game_id')
        result = request.data.get('otb_result')
    
        try:
            game = Game.objects.get(id=game_id)
        except Exception:
            return Response(
                {"result": False,
                 "message": "Game does not exist"},
                status=status.HTTP_404_NOT_FOUND)

        round = Round.objects.get(id=game.round.id)
        tournament = Tournament.objects.get(id=round.tournament.id)

        if tournament.administrativeUser != request.user:
            return Response(
                {"result": False,
                 "message":
                 "Only the user that create the tournament can update it"},
                status=status.HTTP_403_FORBIDDEN)

        game.result = result
        game.finished = True
        game.save()

        return Response(
            {"result": True,
                "message": "Game updated by administrator"},
            status=status.HTTP_200_OK)
