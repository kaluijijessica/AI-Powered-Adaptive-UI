from flask import Flask, render_template, request, jsonify
from datetime import datetime
from transformers import pipeline

app = Flask(__name__)

# Load the Hugging Face zero-shot classification pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define possible command labels the assistant should recognize
LABELS = [
    "set a reminder",
    "call caregiver",
    "ask for help",
    "show time",
    "emergency",
    "unknown"
]

@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.now().strftime("%I:%M %p"))

@app.route('/classify', methods=['POST'])
def classify():
    data = request.json
    transcript = data.get('transcript', '').strip().lower()

    # If transcript is empty
    if not transcript:
        return jsonify({'action': 'unknown', 'message': 'No input received.'})

    # Run AI classification
    result = classifier(transcript, LABELS)
    top_label = result['labels'][0]

    # Prepare response based on top_label
    if top_label == "set a reminder":
        message = "Reminder has been noted: take your medicine."
    elif top_label == "call caregiver":
        message = "Alerting your caregiver now."
    elif top_label == "ask for help":
        message = "Showing help options for you."
    elif top_label == "show time":
        message = f"The current time is {datetime.now().strftime('%I:%M %p')}."
    elif top_label == "emergency":
        message = "Emergency contact triggered!"
    else:
        message = "Sorry, I didn’t catch that."

    return jsonify({
        'action': top_label,
        'message': message
    })

if __name__ == '__main__':
    app.run(debug=True)
