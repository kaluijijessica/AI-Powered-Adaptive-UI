from flask import Flask, render_template
from flask_socketio import SocketIO
from transformers import pipeline
from datetime import datetime
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize AI model
classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=-1
)

COMMAND_CONFIG = {
    'text_size': {
        'labels': ['bigger', 'smaller', 'increase text', 'decrease text'],
        'ui_action': 'adjust_text_size',
        'feedback': {
            'bigger': 'Increasing text size for better readability',
            'smaller': 'Reducing text size for compact view'
        }
    },
    'contrast': {
        'labels': ['higher contrast', 'lower contrast', 'brighter', 'darker'],
        'ui_action': 'adjust_contrast',
        'feedback': {
            'higher': 'Enhancing contrast for clearer viewing',
            'lower': 'Reducing contrast for comfortable reading'
        }
    },
    'time': {
        'labels': ['current time', 'what time is it', 'time'],
        'ui_action': 'show_time',
        'feedback': 'Current time is {time}'
    },
    'emergency': {
        'labels': ['help', 'emergency', 'danger'],
        'ui_action': 'trigger_emergency',
        'feedback': 'Contacting your caregiver Sarah Johnson'
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('voice_command')
def handle_voice_command(data):
    try:
        transcript = data['text'].lower()
        response = None
        
        # Check static matches first
        for category, config in COMMAND_CONFIG.items():
            for label in config['labels']:
                if label in transcript:
                    response = create_response(category, label, config, transcript)
                    break
            if response: break
        
        # AI classification fallback
        if not response:
            result = classifier(
                transcript,
                candidate_labels=list(COMMAND_CONFIG.keys()),
                multi_label=False
            )
            category = result['labels'][0]
            config = COMMAND_CONFIG[category]
            response = create_response(category, transcript, config, transcript)

        socketio.emit('ui_update', response)

    except Exception as e:
        logging.error(f"Processing error: {str(e)}")
        socketio.emit('processing_error', {'message': str(e)})

def create_response(category, label, config, transcript):
    response = {
        'transcript': transcript,
        'category': category,
        'action': config['ui_action'],
        'label': label,
        'timestamp': datetime.now().isoformat()
    }
    
    # Handle feedback
    if isinstance(config['feedback'], dict):
        response['feedback'] = config['feedback'].get(label.split()[0], "Adjustment completed")
    else:
        if '{time}' in config['feedback']:
            response['feedback'] = config['feedback'].format(
                time=datetime.now().strftime('%H:%M')
            )
        else:
            response['feedback'] = config['feedback']
    
    return response

if __name__ == '__main__':
    socketio.run(app, debug=True)