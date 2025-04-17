const socket = io();
const synth = window.speechSynthesis;
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

// Debugging and configuration
const DEBUG_MODE = true;
let isProcessing = false;

// Pre-cache DOM Elements
const micButton = document.getElementById('micButton');
const feedbackEl = document.getElementById('statusFeedback');
const identityDiv = document.getElementById('identityDisplay');
const body = document.body;
const html = document.documentElement;

// Voice setup - optimized to store voice instead of searching each time
let preferredVoice = null;
let voicesLoaded = false;

// Cache computed styles for performance
let currentFontSize = parseFloat(getComputedStyle(document.body).fontSize);

// Speech recognition optimizations
recognition.continuous = false;
recognition.interimResults = false;
recognition.lang = 'en-US';
recognition.maxAlternatives = 1;

// Load voices more efficiently
function loadVoices() {
    const allVoices = synth.getVoices();
    const usVoices = allVoices.filter(v => v.lang === 'en-US');
    
    if (usVoices.length > 0) {
        // Prefer Zira, Microsoft or Google voices
        preferredVoice = usVoices.find(v => v.name.includes('Zira')) || 
                        usVoices.find(v => v.name.includes('Microsoft')) || 
                        usVoices.find(v => v.name.includes('Google')) || 
                        usVoices[0];
        voicesLoaded = true;
        logDebug('Preferred voice selected:', preferredVoice?.name);
    } else {
        setTimeout(loadVoices, 100); // Try again soon
    }
}

// Initialize voices
if (synth.onvoiceschanged !== undefined) {
    synth.onvoiceschanged = loadVoices;
} else {
    loadVoices(); // For browsers that don't fire the event
}

// Speech recognition handlers
micButton.addEventListener('click', () => {
    console.log('Mic button clicked');
    if(!isProcessing) {
        startListening();
    }
});

function startListening() {
    try {
        recognition.start();
        micButton.classList.add('listening');
        isProcessing = true;
        logDebug('🎤 Listening started...');
        updateFeedback("Listening...");
    } catch(e) {
        logDebug('Recognition error on start:', e);
        resetMic();
    }
}

recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript.toLowerCase().trim();
    logDebug(`🎧 Heard: ${transcript}`);
    updateFeedback(`Processing: ${transcript}`);
    
    // Send the command to the server
    console.log('Sending command to server:', transcript);
    socket.emit('process_command', { text: transcript });
};

recognition.onerror = (event) => {
    logDebug(`❌ Recognition error: ${event.error}`);
    updateFeedback("Sorry, I didn't catch that");
    resetMic();
};

recognition.onend = resetMic;

// Socket.IO handlers
socket.on('connect', () => {
    console.log('Socket.IO connected!');
});

socket.on('action_update', (response) => {
    console.log('Action update received:', response);
    logDebug('📡 Server response:', response);
    
    // Ensure feedback exists
    if (!response.feedback) {
        console.warn('No feedback message in response');
        response.feedback = `Executing ${response.action} ${response.direction || ''}`;
    }
    
    updateFeedback(response.feedback);
    
    // Execute action immediately
    executeAction(response);
    
    // Speak feedback after UI updates
    setTimeout(() => speakFeedback(response.feedback), 50);
});

socket.on('error', (error) => {
    logDebug(`⚠️ Server error: ${error.message}`);
    updateFeedback(error.message);
});

socket.on('app_ready', (data) => {
    logDebug('App ready signal received');
    updateFeedback('Ready for voice commands');
});

// FIXED: Support all action types from server
function executeAction(response) {
    logDebug('Executing action:', response);
    
    // Log the exact action and direction for debugging
    console.log('Action execution started:', response.action, response.direction);
    
    // Handle adjust_text_size for backward compatibility
    if (response.action === 'adjust_text_size') {
        response.action = 'adjust_text';
    }
    
    // FIXED HANDLING: Properly handle different action types and directions
    switch (response.action) {
        case 'adjust_contrast':
            console.log('Adjusting contrast to:', response.direction);
            if (response.direction === 'dark') {
                setDarkMode();
            } 
            else if (response.direction === 'light') {
                setLightMode();
            }
            else if (response.direction === 'decrease') {
                // Assume decrease means darker (less light)
                setDarkMode();
            }
            else if (response.direction === 'increase') {
                // Assume increase means lighter (more light)
                setLightMode();
            }
            else {
                // Toggle as fallback
                toggleContrastMode();
            }
            break;
            
        case 'adjust_text':
            console.log('Adjusting text size:', response.direction);
            if (response.direction === 'increase') {
                increaseTextSize();
            } else if (response.direction === 'decrease') {
                decreaseTextSize();
            }
            break;
            
        case 'show_identity':
            console.log('Showing identity');
            showIdentity(response.feedback);
            break;
            
        default:
            console.warn('Unknown action:', response.action);
    }
    
    // Log action to server
    socket.emit('client_log', { message: `Action executed: ${response.action} - ${response.direction || ''}` });
}

// SIMPLIFIED DIRECT FUNCTIONS FOR UI CHANGES

// Set dark mode
function setDarkMode() {
    console.log('Setting dark mode - function called');
    body.className = ''; // Clear all classes
    body.classList.add('dark-mode');
    localStorage.setItem('contrastMode', 'dark');
    console.log('Dark mode applied, body class is now:', body.className);
}

// Set light mode
function setLightMode() {
    console.log('Setting light mode - function called');
    body.className = ''; // Clear all classes
    body.classList.add('light-mode');
    localStorage.setItem('contrastMode', 'light');
    console.log('Light mode applied, body class is now:', body.className);
}

// Toggle contrast mode
function toggleContrastMode() {
    console.log('Toggling contrast mode');
    const currentMode = localStorage.getItem('contrastMode') || 'light';
    if (currentMode === 'light') {
        setDarkMode();
    } else {
        setLightMode();
    }
}

// Expose test functions to the global scope for the test buttons
window.testDarkMode = setDarkMode;
window.testLightMode = setLightMode;
window.testIncreaseText = increaseTextSize;
window.testDecreaseText = decreaseTextSize;

// Increase text size
function increaseTextSize() {
    console.log('Increasing text size - function called');
    currentFontSize = parseFloat(getComputedStyle(document.body).fontSize);
    const newSize = currentFontSize * 1.2;
    document.documentElement.style.fontSize = `${newSize}px`;
    localStorage.setItem('textSize', newSize);
    console.log(`Font size increased to ${newSize}px`);
}

// Decrease text size
function decreaseTextSize() {
    console.log('Decreasing text size - function called');
    currentFontSize = parseFloat(getComputedStyle(document.body).fontSize);
    const newSize = currentFontSize * 0.8;
    document.documentElement.style.fontSize = `${newSize}px`;
    localStorage.setItem('textSize', newSize);
    console.log(`Font size decreased to ${newSize}px`);
}

// Persistent settings initialization
function initializeSettings() {
    console.log('Initializing settings');
    // Set contrast mode
    const savedContrast = localStorage.getItem('contrastMode') || 'light';
    console.log('Saved contrast mode:', savedContrast);
    if (savedContrast === 'dark') {
        setDarkMode();
    } else {
        setLightMode();
    }
    
    // Set text size
    const savedTextSize = localStorage.getItem('textSize');
    if(savedTextSize) {
        document.documentElement.style.fontSize = `${savedTextSize}px`;
        console.log(`Restored font size: ${savedTextSize}px`);
    }
    
    logDebug('Settings initialized');
}

// Voice feedback system
function speakFeedback(text) {
    if(!synth || !voicesLoaded) {
        console.warn('Speech synthesis not available yet');
        return;
    }
    
    try {
        // Cancel any current speech
        if(synth.speaking) synth.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        if (preferredVoice) utterance.voice = preferredVoice;
        utterance.rate = 0.95;
        utterance.pitch = 1.0;
        synth.speak(utterance);
    } catch(error) {
        console.error('Speech failed:', error);
    }
}

// UI functions - optimized
function updateFeedback(message) {
    console.log('Updating feedback with message:', message);
    // Update feedback text
    feedbackEl.textContent = message;
    feedbackEl.classList.remove('hidden');
    
    // Clear any existing timeout
    if (feedbackEl._hideTimeout) {
        clearTimeout(feedbackEl._hideTimeout);
    }
    
    // Set new timeout
    feedbackEl._hideTimeout = setTimeout(() => {
        feedbackEl.classList.add('hidden');
    }, 3000);
}

function resetMic() {
    micButton.classList.remove('listening');
    isProcessing = false;
}

// Debug utilities
function logDebug(...messages) {
    if(DEBUG_MODE) console.log('[DEBUG]', ...messages);
}

function showIdentity(details) {
    console.log('Showing identity details');
    // Update identity display
    identityDiv.innerHTML = `
        <h3>Personal Information</h3>
        <p>${details.replace(/\. /g, '.</p><p>')}</p>
        <button class="close-btn" onclick="this.parentElement.classList.add('hidden')">×</button>
    `;
    identityDiv.classList.remove('hidden');
    
    speakFeedback(details);
    
    // Clear any existing timeout
    if (identityDiv._hideTimeout) {
        clearTimeout(identityDiv._hideTimeout);
    }
    
    // Auto-hide after 1 minute
    identityDiv._hideTimeout = setTimeout(() => {
        identityDiv.classList.add('hidden');
    }, 60000);
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    // Initialize settings first
    initializeSettings();
    
    // Then connect to the server
    socket.emit('connection_init');
    
    // Add direct test button handlers if they exist
    if (document.getElementById('testDark')) {
        document.getElementById('testDark').addEventListener('click', setDarkMode);
    }
    if (document.getElementById('testLight')) {
        document.getElementById('testLight').addEventListener('click', setLightMode);
    }
    if (document.getElementById('testBigger')) {
        document.getElementById('testBigger').addEventListener('click', increaseTextSize);
    }
    if (document.getElementById('testSmaller')) {
        document.getElementById('testSmaller').addEventListener('click', decreaseTextSize);
    }
    
    logDebug('System initialized and ready');
});

// Test function for direct API testing
window.testAction = function(action, direction) {
    executeAction({
        action: action,
        direction: direction,
        feedback: `Testing ${action} - ${direction}`
    });
};