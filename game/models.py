from django.db import models
from django.utils import timezone

class Team(models.Model):
    name = models.CharField(max_length=255)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Flag(models.Model):
    captured_by = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Drapeau capturé par ({self.captured_by})"
        
class Game(models.Model):
    team_a = models.ForeignKey(Team, related_name="team_a", on_delete=models.CASCADE)
    team_b = models.ForeignKey(Team, related_name="team_b", on_delete=models.CASCADE)
    flag = models.OneToOneField(Flag, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Game {self.id} between {self.team_a} and {self.team_b}"
