from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    team = models.IntegerField()
    score = models.IntegerField(default=0) 
    def __str__(self):
        return f"Player {self.id} (User: {self.user})"


class Flag(models.Model):
    captured_by = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Captured by {self.captured_by}" if self.captured_by else "Available"
