const socket = io();
const synth = window.speechSynthesis;
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

// Debugging flags
const DEBUG_MODE = true;
let isProcessing = false;

// Configuration
recognition.continuous = false;
recognition.lang = 'en-US';
recognition.interimResults = false;

// Elements
const micButton = document.getElementById('micButton');
const feedbackEl = document.getElementById('statusFeedback');

// Voice setup
let voices = [];
synth.onvoiceschanged = () => {
    voices = synth.getVoices();
    if(DEBUG_MODE) console.log('Voices loaded:', voices);
};

// Speech recognition handlers
micButton.addEventListener('click', () => {
    if(!isProcessing) {
        recognition.start();
        micButton.classList.add('listening');
        isProcessing = true;
        logDebug('🎤 Listening started...');
    }
});

recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    logDebug(`🎧 Heard: ${transcript}`);
    socket.emit('process_command', { text: transcript });
};

recognition.onerror = (event) => {
    logDebug(`❌ Recognition error: ${event.error}`);
    updateFeedback("Sorry, I didn't catch that");
    resetMic();
};

recognition.onend = () => {
    resetMic();
};

// Socket.IO handlers
socket.on('action_update', (response) => {
    logDebug(`📡 Server response:`, response);
    updateFeedback(response.feedback);
    executeAction(response);
    speakFeedback(response.feedback);
});

socket.on('error', (error) => {
    logDebug(`⚠️ Server error: ${error.message}`);
    updateFeedback(error.message);
});

// Core functions
function executeAction(response) {
    switch(response.action) {
        case 'adjust_text':
            const newSize = response.direction === 'increase' ? 
                parseInt(getComputedStyle(document.body).fontSize) * 1.2 :
                parseInt(getComputedStyle(document.body).fontSize) * 0.8;
            document.documentElement.style.fontSize = `${newSize}px`;
            break;
            
        case 'adjust_contrast':
            document.body.classList.toggle('dark-mode', response.direction === 'dark');
            break;
    }
}

function speakFeedback(text) {
    if(synth.speaking) synth.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = voices.find(v => v.lang === 'en-US') || voices[0];
    synth.speak(utterance);
}

function updateFeedback(message) {
    feedbackEl.textContent = message;
    feedbackEl.classList.remove('hidden');
    setTimeout(() => feedbackEl.classList.add('hidden'), 3000);
}

function resetMic() {
    micButton.classList.remove('listening');
    isProcessing = false;
}

function logDebug(...messages) {
    if(DEBUG_MODE) console.log('[DEBUG]', ...messages);
}

// Initial test
logDebug('Frontend initialized');
socket.emit('test_connection', { timestamp: Date.now() });