from django.urls import path
from . import views

urlpatterns = [
    path('start_game/', views.StartGameView.as_view(), name='start_game'),  # Démarrer la partie
    path('capture_flag/', views.CaptureFlagView.as_view(), name='capture_flag'), # Capturer le drapeau
    path('end_game/', views.EndGameView.as_view(), name='end_game'),  # Terminer la partie
    path('get_scores/<int:game_id>/', views.GetScoresView.as_view(), name='get_scores'),  # URL pour récupérer les scores
    path('restart_game/', views.RestartGameView.as_view(), name='restart_game'),  # Redémarrer la partie
]
