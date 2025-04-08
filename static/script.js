document.addEventListener("DOMContentLoaded", function () {
    const socket = io();
    let lastCommand = null;
    let recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    const micButton = document.getElementById("micButton");
    const status = document.getElementById("status");

    // Function to start listening
    function startListening() {
        console.log("Voice recognition activated...");
        status.textContent = "I'm listening...";
        micButton.classList.add("listening");

        recognition.start();
    }

    // Handle voice recognition result
    recognition.onresult = function (event) {
        const command = event.results[0][0].transcript;
        console.log("User Command:", command);
        status.textContent = `I heard: ${command}`;
        lastCommand = command;

        // Send command to Flask backend
        socket.emit("command", { command: command });
    };

    // Handle errors
    recognition.onerror = function (event) {
        console.error("Recognition error:", event.error);
        status.textContent = "I couldn't hear you. Please try again.";
        micButton.classList.remove("listening");
    };

    recognition.onend = function () {
        micButton.classList.remove("listening");
    };

    // Listen for "Hey" wake word activation from backend
    socket.on("activate_listening", function (data) {
        console.log("Wake word detected:", data.message);
        startListening();
    });

    // Handle response from backend
    socket.on("response", (data) => {
        console.log("Server Response:", data);
        status.textContent = data.message;

        if (data.speak) {
            speak(data.message);
        }

        if (data.size) {
            document.body.style.fontSize = data.size + "px";
        }

        if (data.contrast !== undefined) {
            document.body.classList.toggle("high-contrast", data.contrast);
        }

        if (data.options) {
            const optionsPanel = document.getElementById("optionsPanel");
            optionsPanel.innerHTML = data.options
                .map(
                    (option) =>
                        `<button class="option-button" onclick="handleOption('${option}')">${option}</button>`
                )
                .join("");
            optionsPanel.style.display = "block";
        }
    });

    // Function to trigger speech synthesis
    function speak(text) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        speechSynthesis.speak(utterance);
    }

    // Update time every minute
    function updateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString("en-US", {
            hour: "numeric",
            minute: "2-digit",
            hour12: true,
        });
        const dateString = now.toLocaleDateString("en-US", {
            weekday: "long",
            month: "long",
            day: "numeric",
        });
        document.getElementById("timeDisplay").textContent = `${timeString} on ${dateString}`;
    }

    // Run update time every minute
    updateTime();
    setInterval(updateTime, 60000);

    // Check for medication reminders
    function checkMedication() {
        const now = new Date();
        const hours = now.getHours();
        const minutes = now.getMinutes();

        // Example medication times
        const medTimes = [{ h: 9, m: 0 }, { h: 13, m: 0 }, { h: 18, m: 0 }];

        if (medTimes.some(time => time.h === hours && time.m === minutes)) {
            document.getElementById("reminder").style.display = "block";
            speak("It's time for your medication");
        }
    }

    // Check medication times every minute
    setInterval(checkMedication, 60000);
});
