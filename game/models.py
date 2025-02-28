from datetime import timedelta
from django.db import models
from django.utils import timezone

class Team(models.Model):
    name = models.CharField(max_length=255)
    score = models.IntegerField(default=0)  # Score est basé sur le temps de possession
    total_time_held_flag = models.IntegerField(default=0)  # Nouveau champ pour stocker le temps total passé à détenir le drapeau

    def __str__(self):
        return self.name


class Flag(models.Model):
    captured_by = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField()
    capture_duration = models.DurationField(default=timedelta(0))

    def __str__(self):
        return f"Flag captured by {self.captured_by.name if self.captured_by else 'None'}"


class Game(models.Model):
    team_a = models.ForeignKey(Team, related_name="team_a", on_delete=models.CASCADE)
    team_b = models.ForeignKey(Team, related_name="team_b", on_delete=models.CASCADE)
    flag = models.OneToOneField(Flag, on_delete=models.CASCADE, null=True, blank=True)  # Relier une partie à un drapeau capturé
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Game {self.id} between {self.team_a} and {self.team_b}"
