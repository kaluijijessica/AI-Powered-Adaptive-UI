from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# Hugging Face API settings
API_URL = "https://api-inference.huggingface.co/models/bigscience/bloom"
headers = {"Authorization": "Bearer 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"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process_command', methods=['POST'])
def process_command():
    try:
        command = request.json['command']
        
        # AI prompt for understanding the command
        ai_prompt = f'''Command: "{command}"
            
        Rules:
        - If user wants BIGGER text (examples: "make bigger", "increase", "can't see", "too small") → respond "BIGGER"
        - If user wants SMALLER text (examples: "make smaller", "decrease", "too big") → respond "SMALLER"
        
        Important: The word "bigger" means they want BIGGER text, not smaller.
        
        Respond with single word only: BIGGER or SMALLER'''

        # Call Hugging Face API
        response = requests.post(API_URL, headers=headers, json={"inputs": ai_prompt})
        result = response.json()

        if isinstance(result, list) and len(result) > 0:
            ai_response = result[0]['generated_text'].strip().upper()
            
            # Double-check the response against the command
            command_lower = command.lower()
            if ('big' in command_lower and 'too big' not in command_lower) or \
               'increase' in command_lower or \
               "can't see" in command_lower:
                return jsonify({"action": "BIGGER", "message": "Making the text bigger for you."})
            elif ai_response.find('SMALLER') != -1 or 'too big' in command_lower:
                return jsonify({"action": "SMALLER", "message": "Making the text smaller for you."})
            elif ai_response.find('BIGGER') != -1:
                return jsonify({"action": "BIGGER", "message": "Making the text bigger for you."})
            else:
                return jsonify({"action": "NONE", "message": "Please try saying 'make it bigger' or 'make it smaller'"})
        
        return jsonify({"action": "NONE", "message": "I couldn't understand. Please try again."})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"action": "ERROR", "message": "An error occurred. Please try again."})

if __name__ == '__main__':
    app.run(debug=True)
