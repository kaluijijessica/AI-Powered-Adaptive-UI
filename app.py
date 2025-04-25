from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from transformers import pipeline
import logging
import os
import threading
import time
from functools import lru_cache

# ===== IDENTITY CONFIGURATION =====
IDENTITY_DETAILS = {
    "name": "Jessica Rivers",
    "birth_date": "January 1, 1950",
    "emergency_contact": {
        "name": "Sarah Johnson",
        "relationship": "daughter",
        "phone": "+1 234 567 890"
    },
    "address": "123 Care Street, Avondale, Lusaka, Zambia"
}

# Suppress warnings
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'care-assistant-123'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize classifier - load it once at startup
print("Loading classification model...")
classifier = pipeline(
    "zero-shot-classification",
    model="typeform/distilbert-base-uncased-mnli",
    device=-1  # Force CPU
)
print("Model loaded successfully!")

# FIXED: Consistent action types and directions
VOICE_COMMANDS = {
    # Dark mode commands
    "dark mode": {"action": "adjust_contrast", "direction": "dark", "feedback": "Switching to dark mode"},
    "darker": {"action": "adjust_contrast", "direction": "dark", "feedback": "Switching to dark mode"},
    "night mode": {"action": "adjust_contrast", "direction": "dark", "feedback": "Switching to dark mode"},
    "too bright": {"action": "adjust_contrast", "direction": "dark", "feedback": "Switching to dark mode"},
    "make it darker": {"action": "adjust_contrast", "direction": "dark", "feedback": "Switching to dark mode"},
    
    # Light mode commands
    "light mode": {"action": "adjust_contrast", "direction": "light", "feedback": "Switching to light mode"},
    "brighter": {"action": "adjust_contrast", "direction": "light", "feedback": "Switching to light mode"},
    "day mode": {"action": "adjust_contrast", "direction": "light", "feedback": "Switching to light mode"},
    "too dark": {"action": "adjust_contrast", "direction": "light", "feedback": "Switching to light mode"},
    "make it brighter": {"action": "adjust_contrast", "direction": "light", "feedback": "Switching to light mode"},
    
    # Text size commands - all using adjust_text consistently
    "bigger text": {"action": "adjust_text", "direction": "increase", "feedback": "Making text bigger"},
    "increase text": {"action": "adjust_text", "direction": "increase", "feedback": "Making text bigger"},
    "increase the text": {"action": "adjust_text", "direction": "increase", "feedback": "Making text bigger"},
    "increase text size": {"action": "adjust_text", "direction": "increase", "feedback": "Making text bigger"},
    "text too small": {"action": "adjust_text", "direction": "increase", "feedback": "Making text bigger"},
    "can't read": {"action": "adjust_text", "direction": "increase", "feedback": "Making text bigger"},
    
    "smaller text": {"action": "adjust_text", "direction": "decrease", "feedback": "Making text smaller"},
    "decrease text": {"action": "adjust_text", "direction": "decrease", "feedback": "Making text smaller"},
    "decrease the text": {"action": "adjust_text", "direction": "decrease", "feedback": "Making text smaller"},
    "decrease text size": {"action": "adjust_text", "direction": "decrease", "feedback": "Making text smaller"},
    "text too big": {"action": "adjust_text", "direction": "decrease", "feedback": "Making text smaller"}
}

# Original command configs for fallback
COMMAND_CONFIG = {
    'identity': {
        'labels': [
            "who am i", "what's my name", "tell me about myself",
            "my identity", "my details", "personal information",
            "where do I live", "emergency contact"
        ],
        'action': 'show_identity',
        'responses': {
            'default': "You are {name}, born on {birth_date}. Your emergency contact is {emergency_contact[name]} ({emergency_contact[relationship]}) at {emergency_contact[phone]}. You reside at {address}."
        }
    }
}

# Simplified keywords
IDENTITY_KEYWORDS = ['identity', 'who am', 'my name', 'emergency contact']
FORMATTED_IDENTITY_RESPONSE = None

def initialize_app():
    """Precompute values needed for faster runtime performance"""
    global FORMATTED_IDENTITY_RESPONSE
    
    # Pre-format identity response
    template = COMMAND_CONFIG['identity']['responses']['default']
    FORMATTED_IDENTITY_RESPONSE = template.format(
        name=IDENTITY_DETAILS['name'].strip(),
        birth_date=IDENTITY_DETAILS['birth_date'],
        emergency_contact=IDENTITY_DETAILS['emergency_contact'],
        address=IDENTITY_DETAILS['address']
    )

# Run initialization
initialize_app()

@app.route('/')
def index():
    return render_template('index.html')

# Test route for direct action testing
@app.route('/test/<action>/<direction>')
def test_action(action, direction):
    """Direct test endpoint for UI actions"""
    feedback = "Test action triggered"
    
    if action == "adjust_contrast":
        feedback = f"Switching to {direction} mode"
    elif action == "adjust_text":
        feedback = f"Making text {'bigger' if direction == 'increase' else 'smaller'}"
    
    socketio.emit('action_update', {
        'action': action,
        'direction': direction,
        'feedback': feedback
    })
    
    return "Test sent"

@app.route('/test-ui')
def test_ui():
    return render_template('test.html')

@socketio.on('process_command')
def handle_command(data):
    print(f"\n🔍 Processing command: {data['text']}")
    # Process in a separate thread to avoid blocking
    threading.Thread(target=process_command_thread, args=(data,)).start()

def process_command_thread(data):
    try:
        transcript = data['text'].lower().strip()
        print(f"📝 Command text: {transcript}")
        
        # SIMPLIFIED APPROACH: Direct command matching
        # Check each command to see if it appears in the transcript
        for command, action in VOICE_COMMANDS.items():
            if command in transcript:
                print(f"✅ Matched command: {command}")
                print(f"✅ Sending action: {action}")
                socketio.emit('action_update', action)
                return
                
        # Special handling for common phrases
        if "bright" in transcript:
            print("✅ Detected brightness command")
            if "too" in transcript or "very" in transcript:
                socketio.emit('action_update', {
                    'action': 'adjust_contrast',
                    'direction': 'dark',
                    'feedback': 'Switching to dark mode'
                })
                return
                
        # Check for identity queries
        if any(keyword in transcript for keyword in IDENTITY_KEYWORDS):
            print("🆔 Identity query detected")
            socketio.emit('action_update', {
                'action': 'show_identity',
                'feedback': FORMATTED_IDENTITY_RESPONSE
            })
            return
            
        # If no direct match, use the model as fallback
        print("🤖 No direct match, trying AI classification")
        # Only use identity labels for classification now
        identity_labels = COMMAND_CONFIG['identity']['labels']
        
        result = classifier(transcript, identity_labels)
        top_label = result['labels'][0]
        confidence = result['scores'][0]
        
        if confidence >= 0.35 and top_label in identity_labels:
            print("🆔 AI detected identity query")
            socketio.emit('action_update', {
                'action': 'show_identity',
                'feedback': FORMATTED_IDENTITY_RESPONSE
            })
        else:
            print("❓ Command not recognized")
            socketio.emit('error', {'message': "Let me clarify that"})
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        socketio.emit('error', {'message': "Let's try that again"})

@socketio.on('connection_init')
def handle_init():
    """Send initial settings to client"""
    socketio.emit('app_ready', {'status': 'ok'})

@socketio.on('client_log')
def handle_client_log(data):
    """Log messages from client"""
    print(f"📱 CLIENT: {data['message']}")

if __name__ == '__main__':
    print("🚀 Server starting...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)