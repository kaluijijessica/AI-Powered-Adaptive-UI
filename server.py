from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Flask is working!"

@app.route("/ai-intent", methods=["POST"])
def ai_intent():
    try:
        data = request.json
        user_input = data.get("command")

        if not user_input:
            return jsonify({"error": "No command provided"}), 400

        prompt = f"Analyze this UI command: '{user_input}'. What should change in the UI? Respond with: 'increase text', 'contrast mode', or 'reset'."

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant helping with adaptive UI."},
                {"role": "user", "content": prompt}
            ]
        )

        intent = response["choices"][0]["message"]["content"].strip()
        return jsonify({"intent": intent})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
