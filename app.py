from flask import Flask, request, jsonify
from huggingface_hub import InferenceClient

app = Flask(__name__)

# Use Hugging Face's free text generation API (Runs in the Cloud)
client = InferenceClient(model="bigscience/bloom")

@app.route("/", methods=["GET"])
def home():
    return "Flask is running with Hugging Face API!"

@app.route("/ai-intent", methods=["POST"])
def ai_intent():
    data = request.json
    user_input = data.get("command", "")

    if not user_input:
        return jsonify({"error": "No command provided"}), 400

    try:
        response = client.text_generation(user_input, max_new_tokens=50)
        return jsonify({"intent": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
