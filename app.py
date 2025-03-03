from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from datetime import datetime
import requests
import json

app = Flask(__name__)
socketio = SocketIO(app)

# Hugging Face API settings - using a simpler text classification model
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large"
headers = {"Authorization": "Bearer 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"}

# User preferences and state management
class UserState:
    def __init__(self):
        self.text_size = 16
        self.high_contrast = False
        self.simplified_mode = False
        self.confusion_count = 0
        self.last_interaction = datetime.now()
        self.needs_reminder = False
        self.last_command = None

user_state = UserState()

def process_command(command):
    try:
        command_lower = command.lower()
        
        # Text size commands (keeping the working functionality)
        if any(word in command_lower for word in ['bigger', 'larger', "can't see", 'increase']):
            return "BIGGER"
        elif any(word in command_lower for word in ['smaller', 'decrease', 'too big']):
            return "SMALLER"
            
        # Enhanced contrast detection
        elif any(word in command_lower for word in ['dark', 'bright', 'contrast', 'hard to see', 'better view']):
            return "CONTRAST"
            
        # Time and date queries
        elif any(word in command_lower for word in ['time', 'date', 'day', 'today', 'when']):
            return "TIME"
            
        # Help and confusion
        elif any(word in command_lower for word in ['help', 'confused', 'lost', 'what', 'how']):
            return "HELP"
            
        # Repeat last command
        elif any(word in command_lower for word in ['repeat', 'again', 'what did you say']):
            return "REPEAT"

        # If no direct match, try AI
        prompt = f'''Classify this command: "{command}"
        Options:
        CONTRAST - if about visibility/colors
        TIME - if asking about time/date
        HELP - if needs assistance
        REPEAT - if wants something repeated

        Return only one word from the options above.'''

        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            prediction = result[0]['generated_text'].strip().upper()
            print(f"AI Response: {prediction}")
            
            # Track confusion patterns
            if "confused" in command.lower() or "help" in command.lower():
                user_state.confusion_count += 1
                if user_state.confusion_count >= 3:
                    user_state.simplified_mode = True
            
            return prediction
            
        return "UNCLEAR"
    except Exception as e:
        print(f"Error processing command: {str(e)}")
        return "UNCLEAR"

@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('command')
def handle_command(data):
    try:
        command = data.get('command', '').lower()
        print(f"Received command: {command}")
        
        action = process_command(command)
        print(f"Processed action: {action}")
        
        user_state.last_command = command  # Store last command for repeat functionality
        response = create_response(action, command)
        socketio.emit('response', response)
    except Exception as e:
        print(f"Error in handle_command: {str(e)}")
        socketio.emit('response', {
            "action": "ERROR",
            "message": "I'm having trouble understanding. Could you try again?",
            "speak": True
        })

def create_response(action, command):
    current_time = datetime.now()
    user_state.last_interaction = current_time
    
    if action == "BIGGER":
        user_state.text_size = min(user_state.text_size + 2, 32)
        return {
            "action": "BIGGER",
            "message": "Making the text bigger for you",
            "size": user_state.text_size,
            "speak": True
        }
    elif action == "SMALLER":
        user_state.text_size = max(user_state.text_size - 2, 12)
        return {
            "action": "SMALLER",
            "message": "Making the text smaller for you",
            "size": user_state.text_size,
            "speak": True
        }
    elif action == "CONTRAST":
        user_state.high_contrast = not user_state.high_contrast
        message = "Switching to high contrast mode" if user_state.high_contrast else "Switching to normal contrast"
        return {
            "action": "CONTRAST",
            "message": message,
            "contrast": user_state.high_contrast,
            "speak": True
        }
    elif action == "TIME":
        time_str = current_time.strftime("%I:%M %p on %A, %B %d")
        return {
            "action": "TIME",
            "message": f"It's {time_str}",
            "speak": True,
            "time_display": True
        }
    elif action == "HELP":
        return {
            "action": "HELP",
            "message": "Here's what I can help you with:",
            "options": [
                "Make text bigger",
                "Make text smaller",
                "Change contrast",
                "Tell the time",
                "Repeat last message"
            ],
            "speak": True
        }
    elif action == "REPEAT" and user_state.last_command:
        return create_response(process_command(user_state.last_command), user_state.last_command)
    else:
        return {
            "action": "UNCLEAR",
            "message": "I'm not sure what you need. Try saying:",
            "options": [
                "Make it bigger",
                "Make it smaller",
                "Change contrast",
                "What time is it",
                "Help"
            ],
            "speak": True
        }

if __name__ == '__main__':
    socketio.run(app, debug=True)
