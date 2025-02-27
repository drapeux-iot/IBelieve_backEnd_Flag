let timer;
let gameStarted = false;
let blueScore = 0;
let redScore = 0;
let remainingTime = 60; // 1 minute de jeu
let gameTimeInterval;
let websocket;

const timerElement = document.getElementById("timer");
const gameMessageElement = document.getElementById("game-message");
const blueScoreElement = document.getElementById("blue-score");
const redScoreElement = document.getElementById("red-score");
const startButton = document.getElementById("start-game");
const winnerElement = document.getElementById("winner");

function startGame() {
  if (gameStarted) return;

  gameStarted = true;
  gameMessageElement.textContent = "Le jeu est en cours...";

  // Démarre le timer
  startTimer();

  // Ouvre la connexion WebSocket pour recevoir les notifications en temps réel
  websocket = new WebSocket('ws://localhost:8000/ws/game/4/');  // Remplacer l'URL par celle de ton WebSocket Django

  websocket.onopen = () => {
    console.log("WebSocket connecté");
  };

  websocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleGameEvent(data.message);
  };

  websocket.onerror = (error) => {
    console.error("Erreur WebSocket:", error);
  };

  websocket.onclose = () => {
    console.log("WebSocket fermé");
  };

  startButton.disabled = true;
}

function startTimer() {
  gameTimeInterval = setInterval(() => {
    if (remainingTime <= 0) {
      clearInterval(gameTimeInterval);
      gameMessageElement.textContent = "Le jeu est terminé!";
      determineWinner();
      return;
    }

    remainingTime--;
    const minutes = Math.floor(remainingTime / 60);
    const seconds = remainingTime % 60;
    timerElement.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }, 1000);
}

function handleGameEvent(message) {
  // Met à jour le score et le message selon le message reçu
  if (message.includes("Équipe Bleue")) {
    blueScore++;
    blueScoreElement.textContent = blueScore;
  } else if (message.includes("Équipe Rouge")) {
    redScore++;
    redScoreElement.textContent = redScore;
  }

  // Vérifie si une équipe a gagné
  determineWinner();
}

function determineWinner() {
  if (blueScore > redScore) {
    winnerElement.textContent = "L'ÉQUIPE BLEUE A GAGNÉ!";
    winnerElement.style.color = "blue";
  } else if (redScore > blueScore) {
    winnerElement.textContent = "L'ÉQUIPE ROUGE A GAGNÉ!";
    winnerElement.style.color = "red";
  } else {
    winnerElement.textContent = "ÉGALITÉ!";
    winnerElement.style.color = "gray";
  }
}
