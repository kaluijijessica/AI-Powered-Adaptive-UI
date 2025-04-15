from flask import Flask, render_template
from flask_socketio import SocketIO
from transformers import pipeline
import logging
import os

# Suppress warnings
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'care-assistant-123'
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Debugging classifier
classifier = pipeline(
    "zero-shot-classification",
    model="typeform/distilbert-base-uncased-mnli",
    device=-1  # Force CPU
)

COMMAND_CONFIG = {
    'text_size': {
        'labels': ['bigger text', 'smaller text', 'increase size', 'decrease size'],
        'action': 'adjust_text',
        'responses': {
            'increase': 'Text enlarged',
            'decrease': 'Text reduced'
        }
    },
    'contrast': {
        'labels': ['dark mode', 'light mode', 'toggle contrast'],
        'action': 'adjust_contrast',
        'responses': {
            'dark': 'Dark mode activated',
            'light': 'Light mode activated',
            'toggle': 'Contrast changed'
        }
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('process_command')
def handle_command(data):
    try:
        print(f"\n🔧 RAW INPUT: {data['text']}")
        transcript = data['text'].lower().strip()
        
        # Force test command
        if "test" in transcript:
            print("🔥 TEST COMMAND RECEIVED")
            socketio.emit('action_update', {
                'action': 'adjust_text',
                'direction': 'increase',
                'feedback': 'Test successful!'
            })
            return

        # Real classification
        candidate_labels = [label for config in COMMAND_CONFIG.values() for label in config['labels']]
        result = classifier(transcript, candidate_labels)
        print(f"🎯 CLASSIFICATION RESULT: {result}")
        
        if result['scores'][0] < 0.4:
            raise ValueError("Low confidence")
            
        top_label = result['labels'][0]
        print(f"🏆 BEST MATCH: {top_label}")

        # Find matching action
        response = None
        for category, config in COMMAND_CONFIG.items():
            if top_label in config['labels']:
                direction = 'increase' if 'bigger' in top_label or 'increase' in top_label else 'decrease'
                response = {
                    'action': config['action'],
                    'direction': direction,
                    'feedback': config['responses'][direction]
                }
                break

        if response:
            print(f"🚀 SENDING RESPONSE: {response}")
            socketio.emit('action_update', response)
        else:
            raise ValueError("No matching command")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        socketio.emit('error', {'message': "Let's try that again"})

if __name__ == '__main__':
    print("🚀 Server starting...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)