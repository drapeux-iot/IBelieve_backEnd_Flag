from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Game, Team, Flag
import json
from datetime import timedelta
from channels.layers import get_channel_layer


# Variables globales pour le score et l'état de la partie
game_started = False
current_game = None  # Partie en cours

@csrf_exempt
def start_game(request):
    global game_started, current_game
    if request.method == 'POST':
        game_started = True

        # Supprimer toutes les équipes existantes avant de commencer une nouvelle partie
        Team.objects.all().delete()
        # Créer les équipes en premier
        team_blue = Team.objects.create(name="Blue", score=0)
        team_red = Team.objects.create(name="Red", score=0)

        # Ensuite, créer la partie avec les équipes assignées dès la création
        current_game = Game.objects.create(
            start_time=timezone.now(),
            team_a=team_blue,
            team_b=team_red
        )

        return JsonResponse({'message': 'Jeu démarré'})
    
    return JsonResponse({'message': 'Méthode non supportée'}, status=405)



@csrf_exempt
def capture_flag(request):
    global current_game, game_started
    if request.method == 'POST':
        if not current_game or not game_started:
            return JsonResponse({'message': 'La partie n\'a pas encore commencé'}, status=400)

        data = json.loads(request.body)
        team_name = data.get('team')

        if team_name == "Blue":
            team = current_game.team_a
        elif team_name == "Red":
            team = current_game.team_b
        else:
            return JsonResponse({'message': 'Équipe non valide'}, status=400)

        now = timezone.now()

        if current_game.flag:
            previous_team = current_game.flag.captured_by

            if previous_team:
                previous_capture_duration = now - current_game.flag.timestamp
                current_game.flag.capture_duration += previous_capture_duration
                current_game.flag.save()

                if previous_team == current_game.team_a:
                    current_game.team_a.total_time_held_flag += previous_capture_duration.total_seconds()
                    current_game.team_a.save()
                elif previous_team == current_game.team_b:
                    current_game.team_b.total_time_held_flag += previous_capture_duration.total_seconds()
                    current_game.team_b.save()

            # Assigner le drapeau à la nouvelle équipe
            current_game.flag.captured_by = team
            current_game.flag.timestamp = now
            current_game.flag.save()
        else:
            # Création du drapeau
            current_game.flag = Flag.objects.create(captured_by=team, timestamp=now, capture_duration=timedelta(0))
            current_game.save()

        # Notification via WebSocket
        channel_layer = get_channel_layer()
        team_name_message = f"{team_name} a capturé le drapeau !"
        
        # Envoi du message au groupe WebSocket
        channel_layer.group_send(
            'flag_updates',  # Le nom du groupe défini dans le consumer
            {
                'type': 'flag_status',
                'team': team_name_message
            }
        )

        return JsonResponse({'message': f'Drapeau capturé par l\'équipe {team_name}'})

    return JsonResponse({'message': 'Méthode non supportée'}, status=405)



@csrf_exempt
def end_game(request):
    global game_started, current_game
    if request.method == 'POST':
        if not current_game or not game_started:
            return JsonResponse({'message': 'Aucune partie en cours ou déjà terminée'}, status=400)

        # Marquer la partie comme terminée
        game_started = False  
        now = timezone.now()
        current_game.end_time = now  # Met à jour l'heure de fin

        # Calcul du temps total de possession pour chaque équipe
        blue_team_duration = current_game.team_a.total_time_held_flag
        red_team_duration = current_game.team_b.total_time_held_flag

        # Ajouter le temps de possession en cours
        if current_game.flag and current_game.flag.captured_by:
            last_capture_duration = (now - current_game.flag.timestamp).total_seconds()
            if current_game.flag.captured_by == current_game.team_a:
                blue_team_duration += last_capture_duration
            else:
                red_team_duration += last_capture_duration

        # Déterminer le gagnant
        if blue_team_duration > red_team_duration:
            winner = current_game.team_a
            winner_name = "Blue"
        elif red_team_duration > blue_team_duration:
            winner = current_game.team_b
            winner_name = "Red"
        else:
            winner = None
            winner_name = "Égalité"

        current_game.winner = winner
        current_game.save()  # Sauvegarde après mise à jour de `end_time` et `winner`

        return JsonResponse({
            'message': 'Partie terminée',
            'scores': {
                "Blue": blue_team_duration,
                "Red": red_team_duration
            },
            'winner': winner_name
        })

    return JsonResponse({'message': 'Méthode non supportée'}, status=405)


def get_scores(request):
    global current_game

    if current_game:
        flag = current_game.flag  # Récupérer le drapeau associé à la partie en cours

        # Initialiser les durées de possession
        blue_team_duration = timedelta(0)
        red_team_duration = timedelta(0)

        if flag and flag.captured_by:
            # Ajouter la durée déjà comptabilisée
            if flag.captured_by == current_game.team_a:
                blue_team_duration = flag.capture_duration
            elif flag.captured_by == current_game.team_b:
                red_team_duration = flag.capture_duration

            # Ajouter la durée en cours si la partie est active et que le drapeau est encore capturé
            if game_started:
                time_since_last_capture = timezone.now() - flag.timestamp
                if flag.captured_by == current_game.team_a:
                    blue_team_duration += time_since_last_capture
                elif flag.captured_by == current_game.team_b:
                    red_team_duration += time_since_last_capture

        return JsonResponse({
            'scores': {
                "Blue": current_game.team_a.score,
                "Red": current_game.team_b.score
            },
            'capture_durations': {
                "Blue": str(blue_team_duration),
                "Red": str(red_team_duration)
            }
        })

    return JsonResponse({'message': 'Aucune partie en cours'}, status=400)


