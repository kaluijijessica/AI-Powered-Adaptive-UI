from flask import Flask, request, jsonify
import os
from openai import OpenAI  # Import the new OpenAI client
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Make sure it's set in your .env file.")

client = OpenAI(api_key=api_key)  # Initialize OpenAI client

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Flask is running!"

@app.route("/ai-intent", methods=["POST"])
def ai_intent():
    data = request.json  # Get JSON data
    user_input = data.get("command", "")

    if not user_input:
        return jsonify({"error": "No command provided"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant helping with adaptive UI."},
                {"role": "user", "content": f"Analyze this UI command: '{user_input}'. What should change in the UI?"}
            ]
        )
        intent = response.choices[0].message.content.strip()
        return jsonify({"intent": intent})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
