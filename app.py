from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from datetime import datetime
import requests
import json

app = Flask(__name__)
socketio = SocketIO(app)

# Hugging Face API settings
API_URL = "https://api-inference.huggingface.co/models/distilbert-base-uncased"
headers = {"Authorization": "Bearer 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"}

# User preferences and state management
class UserState:
    def __init__(self):
        self.text_size = 16
        self.high_contrast = False
        self.last_interaction = None
        self.confusion_count = 0
        self.needs_reminder = False

user_state = UserState()

def process_command(command):
    try:
        # Create a clear prompt for the model
        prompt = f'''Command: "{command}"
        Rules:
        - If about making text bigger/increasing size → respond "BIGGER"
        - If about making text smaller/decreasing size → respond "SMALLER"
        - If about time/date/when → respond "TIME"
        - If about help/confused → respond "HELP"
        - If about contrast/visibility → respond "CONTRAST"
        Respond with single word only from above options.'''

        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            prediction = result[0]['generated_text'].strip().upper()
            return prediction
        return "UNCLEAR"
    except Exception as e:
        print(f"Error: {str(e)}")
        return "UNCLEAR"

@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('command')
def handle_command(data):
    command = data.get('command', '').lower()
    action = process_command(command)
    response = create_response(action, command)
    socketio.emit('response', response)

def create_response(action, command):
    current_time = datetime.now()
    
    if action == "HELP":
        return {
            "action": "HELP",
            "message": "It's okay to feel confused. Would you like me to:",
            "options": [
                "Make the text easier to read",
                "Tell you the time and date",
                "Read the text out loud"
            ],
            "speak": True
        }

    elif action == "TIME":
        time_str = current_time.strftime("%I:%M %p on %A, %B %d")
        return {
            "action": "TIME",
            "message": f"It's {time_str}",
            "speak": True
        }

    elif action == "BIGGER":
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
        return {
            "action": "CONTRAST",
            "message": "Adjusting the contrast to make it easier to read",
            "contrast": user_state.high_contrast,
            "speak": True
        }

    else:
        return {
            "action": "UNCLEAR",
            "message": "I'm not sure what you need. Would you like me to:",
            "options": [
                "Make the text bigger",
                "Make the text smaller",
                "Change the contrast",
                "Tell you the time"
            ],
            "speak": True
        }

if __name__ == '__main__':
    socketio.run(app, debug=True)
