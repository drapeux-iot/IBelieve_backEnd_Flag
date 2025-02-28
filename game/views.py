from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Game, Team, Flag
import json
from datetime import timedelta


# Variables globales pour le score et l'état de la partie
game_started = False
current_game = None  # Partie en cours

@csrf_exempt
def start_game(request):
    global game_started, current_game
    if request.method == 'POST':
        game_started = True

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
    global current_game
    if request.method == 'POST':
        if not current_game:
            return JsonResponse({'message': 'La partie n\'a pas encore commencé'}, status=400)

        data = json.loads(request.body)
        team_name = data.get('team')

        # Récupération de l'équipe
        if team_name == "Blue":
            team = current_game.team_a
        elif team_name == "Red":
            team = current_game.team_b
        else:
            return JsonResponse({'message': 'Équipe non valide'}, status=400)

        now = timezone.now()

        # Vérifier si un drapeau est déjà capturé
        if current_game.flag:
            previous_team = current_game.flag.captured_by

            # Calculer la durée de possession de l'équipe précédente
            if previous_team:
                previous_capture_duration = now - current_game.flag.timestamp

                # Ajouter la durée au temps total de l'équipe précédente
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
            # Si aucun drapeau n'existe, en créer un
            current_game.flag = Flag.objects.create(captured_by=team, timestamp=now)
            current_game.save()

        return JsonResponse({
            'message': f'Drapeau capturé par l\'équipe {team_name}',
        })

    return JsonResponse({'message': 'Méthode non supportée'}, status=405)



@csrf_exempt
def end_game(request):
    global game_started, current_game
    if request.method == 'POST':
        if not current_game:
            return JsonResponse({'message': 'Aucune partie en cours'}, status=400)

        game_started = False
        now = timezone.now()

        # Récupérer le temps total de possession stocké
        blue_team_duration = current_game.team_a.total_time_held_flag
        red_team_duration = current_game.team_b.total_time_held_flag

        # Si le drapeau est actuellement détenu, ajouter la durée de possession en cours
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

        # Mettre à jour la partie
        current_game.end_time = now
        current_game.winner = winner
        current_game.save()

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


