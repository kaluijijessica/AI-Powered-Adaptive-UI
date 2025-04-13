let recognition;
let isListening = false;

// Check for browser support
if ('webkitSpeechRecognition' in window) {
  recognition = new webkitSpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = false;
  recognition.lang = 'en-US';

  recognition.onstart = () => {
    isListening = true;
    document.querySelector('.status-message').innerText = "Listening...";
  };

  recognition.onend = () => {
    isListening = false;
    document.querySelector('.status-message').innerText = "Click 'Speak' or say 'Hello Assistant' to talk.";
    // Auto-restart if listening mode is active
    setTimeout(() => {
      if (!isListening) {
        recognition.start();
      }
    }, 1000);
  };

  recognition.onresult = (event) => {
    const transcript = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
    console.log("Recognized:", transcript);

    if (transcript.includes("hello assistant") || transcript.includes("hey assistant")) {
      document.querySelector('.status-message').innerText = "How can I assist you?";
    } else {
      processCommand(transcript);
    }
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
    document.querySelector('.status-message').innerText = "Error: " + event.error;
  };

  // Start listening by default
  recognition.start();
} else {
  alert("Your browser does not support speech recognition.");
}

// Manual trigger
function toggleSpeechRecognition() {
  if (isListening) {
    recognition.stop();
  } else {
    recognition.start();
  }
}

// Interpret speech and adapt UI
function processCommand(transcript) {
  const reminder = document.querySelector('.reminder');
  const options = document.querySelector('.options-panel');
  const caregiver = document.querySelector('.caregiver-panel');

  if (transcript.includes("remind me") || transcript.includes("reminder")) {
    reminder.style.display = "block";
    reminder.innerText = "Don't forget your medication at 6 PM.";
    options.style.display = "none";
    caregiver.style.display = "none";
  } else if (transcript.includes("help")) {
    options.style.display = "block";
    reminder.style.display = "none";
    caregiver.style.display = "none";
  } else if (transcript.includes("caregiver") || transcript.includes("emergency")) {
    caregiver.style.display = "block";
    options.style.display = "none";
    reminder.style.display = "none";
  } else {
    reminder.style.display = "none";
    options.style.display = "none";
    caregiver.style.display = "none";
    document.querySelector('.status-message').innerText = `I didn't understand. Please try again.`;
  }
}

// Attach manual button trigger
document.getElementById('speakButton').addEventListener('click', toggleSpeechRecognition);
