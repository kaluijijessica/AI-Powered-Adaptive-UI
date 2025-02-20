function sendToAI(command) {
    fetch("http://127.0.0.1:5000/ai-intent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: command })
    })
    .then(response => response.json())
    .then(data => {
        updateUI(data.intent);
    })
    .catch(error => console.error("Error:", error));
}
