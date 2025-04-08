from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from datetime import datetime
import requests
import json
import speech_recognition as sr
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# Hugging Face API settings - using a pre-trained model for command classification
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
    """
    Use the Hugging Face AI model as the primary classifier.
    The prompt includes all options so that context is properly analyzed.
    In case the response is unclear, fallback to keyword matching.
    """
    try:
        prompt = f'''You are an assistant that receives voice commands from dementia patients.
Interpret the following command and return one of the following actions:
- BIGGER: if the user wants the text to be increased.
- SMALLER: if the user wants the text to be decreased.
- CONTRAST: if the user wants to adjust contrast (e.g., "too bright" means switch to dark mode).
- TIME: if the user is asking for the current time/date.
- HELP: if the user is asking for help.
- REPEAT: if the user wants the last command repeated.
Command: "{command}"
Respond with only one of these words.
'''
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0 and 'generated_text' in result[0]:
            prediction = result[0]['generated_text'].strip().upper()
            print(f"AI Response: {prediction}")
            # If the AI returns a valid action, use it.
            if prediction in ["BIGGER", "SMALLER", "CONTRAST", "TIME", "HELP", "REPEAT"]:
                return prediction

        # Fallback: keyword matching if AI response is unclear
        command_lower = command.lower()
        if any(word in command_lower for word in ['bigger', 'larger', "can't see", 'increase']):
            return "BIGGER"
        elif any(word in command_lower for word in ['smaller', 'decrease', 'too big']):
            return "SMALLER"
        elif any(word in command_lower for word in ['dark', 'bright', 'contrast', 'hard to see', 'too bright', 'better view']):
            return "CONTRAST"
        elif any(word in command_lower for word in ['time', 'date', 'day', 'today', 'when']):
            return "TIME"
        elif any(word in command_lower for word in ['help', 'confused', 'lost', 'what', 'how']):
            return "HELP"
        elif any(word in command_lower for word in ['repeat', 'again', 'what did you say']):
            return "REPEAT"
        else:
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
        
        # Process command using AI classifier (primary)
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
        # Recursively process the last command for context.
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

def listen_for_wake_word():
    """ Continuously listens for the wake word "hello" using the microphone. """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Background wake word listener started...")
        while True:
            try:
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio).lower()
                print(f"Background heard: {text}")
                if "hello" in text:
                    print("Wake word 'hello' detected in background!")
                    socketio.emit('wake_word_detected', {"message": "Wake word activated!"})
                    # Optionally, auto-trigger listening:
                    # startListening() could be invoked here if desired.
            except sr.UnknownValueError:
                continue  # Ignore unrecognized speech
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")

# Start the background thread for wake word detection
wake_word_thread = threading.Thread(target=listen_for_wake_word, daemon=True)
wake_word_thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True)
