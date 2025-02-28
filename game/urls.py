from django.urls import path
from . import views

urlpatterns = [
    path('start_game/', views.start_game, name='start_game'),
    path('capture_flag/', views.capture_flag, name='capture_flag'),
    path('end_game/', views.end_game, name='end_game'),
    path('get_scores/', views.get_scores, name='get_scores'),
]
