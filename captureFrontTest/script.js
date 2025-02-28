const baseUrl = "http://localhost:8000"; // Ajuste si nécessaire

async function startGame() {
    const response = await fetch(`${baseUrl}/start_game/`, { method: "POST" });
    const data = await response.json();
    document.getElementById("message").innerText = data.message;
    updateScores();
}

async function captureFlag(team) {
    const response = await fetch(`${baseUrl}/capture_flag/`, {
        method: "POST",
        body: JSON.stringify({ team: team }),
        headers: { "Content-Type": "application/json" }
    });

    const data = await response.json();
    document.getElementById("message").innerText = data.message;
    updateScores();
}

async function endGame() {
    const response = await fetch(`${baseUrl}/end_game/`, { method: "POST" });
    const data = await response.json();
    document.getElementById("message").innerText = data.message;

    if (data.scores) {
        document.getElementById("blue-score").innerText = data.scores.Blue;
        document.getElementById("red-score").innerText = data.scores.Red;
    }
}

async function updateScores() {
    const response = await fetch(`${baseUrl}/get_scores/`);
    const data = await response.json();

    if (data.scores) {
        document.getElementById("blue-score").innerText = data.scores.Blue;
        document.getElementById("red-score").innerText = data.scores.Red;
    }
}
