# Drapeau Connecté

## Description
Drapeau Connecté est un jeu en ligne où deux équipes s'affrontent pour capturer un drapeau. Ce projet utilise Django pour le backend et les WebSockets pour la communication en temps réel.

## Installation

1. Clonez le dépôt :
    ```bash
    git clone https://github.com/votre-utilisateur/drapeau-connecte.git
    cd drapeau-connecte
    ```

2. Créez et activez un environnement virtuel :
    ```bash
    python -m venv env
    env\Scripts\activate  # Sur Windows
    ```

3. Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

4. Appliquez les migrations :
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. Lancez le serveur de développement :
    ```bash
    python manage.py runserver
    ```

## Utilisation

### Démarrer une partie
Envoyez une requête POST à `/start_game/` avec les IDs des deux équipes :
```json
{
    "team_a": 1,
    "team_b": 2
}
```

### Capturer le drapeau
Envoyez une requête POST à `/capture_flag/` avec l'ID du jeu et le nom de l'équipe :
```json
{
    "game_id": 1,
    "team": "Red"
}
```

### Terminer une partie
Envoyez une requête POST à `/end_game/` avec l'ID du jeu :
```json
{
    "game_id": 1
}
```

### Obtenir les scores
Envoyez une requête GET à `/get_scores/{game_id}/` pour obtenir les scores des équipes et le gagnant :
```json
{
    "game_id": 1,
    "team_a": {
        "name": "Red",
        "score": 3
    },
    "team_b": {
        "name": "Blue",
        "score": 2
    },
    "winner": "Red"
}
```

### Redémarrer une partie
Envoyez une requête POST à `/restart_game/` avec l'ID du jeu :
```json
{
    "game_id": 1
}
```

## Structure du Projet

```
CaptureFlag/
├── CaptureFlag/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── ...
├── game/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── migrations/
│       └── __init__.py
├── manage.py
└── README.md
```
