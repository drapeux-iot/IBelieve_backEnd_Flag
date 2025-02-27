from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Game, Flag, Team
from django.utils import timezone
from django.db import transaction
from channels.layers import get_channel_layer
import logging

logger = logging.getLogger(__name__)

class StartGameView(APIView):
    def post(self, request, format=None):
        team_a = Team.objects.get(id=request.data['team_a'])
        team_b = Team.objects.get(id=request.data['team_b'])
        
        # Réinitialiser les scores à 0 pour les deux équipes
        team_a.score = 0
        team_b.score = 0
        team_a.save()
        team_b.save()

        # Créer un flag pour la partie
        flag = Flag.objects.create()

        # Créer un objet Game avec les deux équipes et le flag
        game = Game.objects.create(team_a=team_a, team_b=team_b, flag=flag)

        # Notification à travers le canal pour démarrer la partie
        channel_layer = get_channel_layer()
        message = {"message": "La partie a démarré", "game_id": game.id}
        
        channel_layer.group_send(
            f"game_{game.id}",
            {
                "type": "send_to_game",
                "message": message
            }
        )

        return Response({"message": "Partie lancée", "game_id": game.id}, status=status.HTTP_201_CREATED)

class CaptureFlagView(APIView):
    def post(self, request, format=None):
        game_id = request.data.get('game_id')
        team_name = request.data.get('team')

        game = Game.objects.get(id=game_id)
        team = Team.objects.get(name=team_name)
        
        with transaction.atomic():
            flag = game.flag
            flag.captured_by = team
            flag.timestamp = timezone.now()
            flag.save()

            if team == game.team_a:
                game.team_a.score += 1
                game.team_a.save()  # Sauvegarder l'objet Team
            elif team == game.team_b:
                game.team_b.score += 1
                game.team_b.save()  # Sauvegarder l'objet Team
            game.save()

        logger.info(f"Scores après capture: Team A - {game.team_a.score}, Team B - {game.team_b.score}")

        channel_layer = get_channel_layer()
        message = {
            "message": f"Drapeau capturé par l'équipe {team_name} !",
            "game_id": game_id,
            "team_a_score": game.team_a.score,
            "team_b_score": game.team_b.score
        }
        channel_layer.group_send(
            f"game_{game_id}",
            {
                "type": "send_to_game",
                "message": message
            }
        )

        return Response({"message": f"Drapeau capturé par l'équipe {team_name}!", "scores": {
            "team_a": game.team_a.score,
            "team_b": game.team_b.score
        }}, status=status.HTTP_200_OK)

from django.utils import timezone

class EndGameView(APIView):
    def post(self, request, format=None):
        game = Game.objects.get(id=request.data['game_id'])
        
        game.end_time = timezone.now()

        # Déterminer le gagnant
        if game.team_a.score > game.team_b.score:
            game.winner = game.team_a
        elif game.team_a.score < game.team_b.score:
            game.winner = game.team_b
        else:
            game.winner = None  # Si égalité

        game.save()

        # Envoi de message sur le canal
        channel_layer = get_channel_layer()
        message = {
            "message": f"Partie terminée. Gagnant: {game.winner.name if game.winner else 'Égalité'}",
            "game_id": game.id,
            "team_a_score": game.team_a.score,
            "team_b_score": game.team_b.score,
            "end_time": game.end_time
        }
        channel_layer.group_send(
            f"game_{game.id}",
            {
                "type": "send_to_game",
                "message": message
            }
        )

        return Response({
            "message": f"Partie terminée. Gagnant: {game.winner.name if game.winner else 'Égalité'}",
            "end_time": game.end_time,
            "team_a_score": game.team_a.score,
            "team_b_score": game.team_b.score
        }, status=status.HTTP_200_OK)


class GetScoresView(APIView):
    def get(self, request, game_id, format=None):
        try:
            game = Game.objects.get(id=game_id)
            team_a_score = game.team_a.score
            team_b_score = game.team_b.score

            return Response({
                "game_id": game.id,
                "team_a": {
                    "name": game.team_a.name,
                    "score": team_a_score
                },
                "team_b": {
                    "name": game.team_b.name,
                    "score": team_b_score
                },
                "winner" : game.winner.name if game.winner else None
            }, status=status.HTTP_200_OK)
        except Game.DoesNotExist:
            return Response({"error": "Partie non trouvée"}, status=status.HTTP_404_NOT_FOUND)

class RestartGameView(APIView):
    async def post(self, request, format=None):
        game_id = request.data.get('game_id')
        try:
            game = Game.objects.get(id=game_id)
            game.team_a.score = 0
            game.team_b.score = 0
            game.flag.captured_by = None
            game.flag.timestamp = None
            game.flag.save()
            game.start_time = timezone.now()
            game.end_time = None
            game.save()

            channel_layer = get_channel_layer()
            message = {"message": "La partie a été redémarrée", "game_id": game.id}
            await channel_layer.group_send(
                f"game_{game.id}",
                {
                    "type": "send_to_game",
                    "message": message
                }
            )

            return Response({"message": "Partie redémarrée", "game_id": game.id}, status=status.HTTP_200_OK)
        except Game.DoesNotExist:
            return Response({"error": "Partie non trouvée"}, status=status.HTTP_404_NOT_FOUND)