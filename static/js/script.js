const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.continuous = false;
recognition.lang = 'en-US';

// DOM Elements
const micButton = document.getElementById('micButton');
const processingStages = {
    stage1: document.getElementById('stage1'),
    stage2: document.getElementById('stage2'),
    stage3: document.getElementById('stage3'),
    stage4: document.getElementById('stage4')
};
const heardCommand = document.getElementById('heardCommand');
const classificationResult = document.getElementById('classificationResult');
const actionFeedback = document.getElementById('actionFeedback');
const dynamicTime = document.getElementById('dynamicTime');
const emergencyPanel = document.getElementById('emergencyPanel');
const socket = io();

// Voice Handling
micButton.addEventListener('click', () => {
    if (!recognition.recording) {
        resetStages();
        recognition.start();
        updateStage('stage1', true);
        updateStage('stage2', true);
    }
});

recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    heardCommand.textContent = transcript;
    socket.emit('voice_command', { text: transcript });
};

// Socket.IO Handlers
socket.on('ui_update', (response) => {
    updateStage('stage3', true);
    classificationResult.textContent = response.category.replace('_', ' ').toUpperCase();
    
    setTimeout(() => {
        updateStage('stage4', true);
        actionFeedback.textContent = response.feedback;
        applyUIModifications(response);
        speakFeedback(response.feedback);
    }, 1000);
});

socket.on('processing_error', (error) => {
    showError(error.message);
    resetStages();
});

// UI Modifications
function applyUIModifications(response) {
    const adaptiveTexts = document.querySelectorAll('[data-adaptive-type="text"]');
    
    switch(response.action) {
        case 'adjust_text_size':
            const newSize = response.label.includes('bigger') ? 'var(--font-large)' : 'var(--font-normal)';
            adaptiveTexts.forEach(el => {
                el.style.fontSize = newSize;
                el.style.color = response.label.includes('bigger') ? 'var(--high-contrast)' : 'var(--text-color)';
            });
            break;

        case 'adjust_contrast':
            document.body.classList.toggle('high-contrast');
            break;

        case 'show_time':
            dynamicTime.textContent = response.feedback.split(': ')[1];
            document.getElementById('timeDisplay').classList.remove('hidden');
            break;

        case 'trigger_emergency':
            emergencyPanel.classList.remove('hidden');
            setTimeout(() => {
                emergencyPanel.classList.add('hidden');
            }, 5000);
            break;
    }
}

// Feedback System
function speakFeedback(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1.1;
    speechSynthesis.speak(utterance);
}

// Stage Management
function updateStage(stageId, active) {
    processingStages[stageId].classList.toggle('active', active);
}

function resetStages() {
    Object.values(processingStages).forEach(stage => {
        stage.classList.remove('active');
        const textElement = stage.querySelector('.stage-text');
        if (textElement) textElement.textContent = stage.dataset.default;
    });
}

// Error Handling
function showError(message) {
    const errorPanel = document.getElementById('errorPanel');
    errorPanel.querySelector('.error-message').textContent = message;
    errorPanel.setAttribute('aria-hidden', 'false');
    
    setTimeout(() => {
        errorPanel.setAttribute('aria-hidden', 'true');
    }, 5000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    recognition.start();
    setInterval(() => {
        document.getElementById('currentTime').textContent = 
            new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }, 1000);
});