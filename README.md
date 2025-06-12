
---

# AI-Powered Adaptive UI for Dementia Patients

## **Project Overview**

This project is an AI-powered adaptive user interface designed to assist dementia patients by providing voice-activated commands and dynamic UI adjustments. The assistant listens for commands, classifies them using an AI model, and adapts the UI in real time to improve accessibility and usability.

### **Key Features**

1. **Voice Command Recognition**:
   - The assistant listens for voice commands like "make text bigger," "change contrast," or "what time is it."
   - Commands are processed using a zero-shot classification model.

2. **Wake Word Detection**:
   - The assistant can be activated by saying the wake word "hello" or clicking the "Speak" button.

3. **Dynamic UI Adaptation**:
   - The UI adjusts text size, toggles high-contrast mode, displays the current time, and provides identity information based on user commands.

4. **Identity Information**:
   - The assistant can provide personal details like name, birth date, emergency contact, and address.

5. **Schedule Management**:
   - Displays the user's daily schedule and reminders.

6. **Caregiver Support**:
   - Includes features like a caregiver dashboard and emergency buttons.

---

## **How to Run the Project**

### **Prerequisites**

1. **Python**: Ensure Python 3.8 or higher is installed.
2. **Dependencies**: Install the required Python packages using `pip`.
3. **Environment Variables**:
   - Create a .env file in the project directory to store sensitive keys (e.g., Hugging Face API key).

### **Setup Instructions**

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/kaluijijessica/AI-Powered-Adaptive-UI.git
   cd ai-powered-adaptive-ui
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   - Create a .env file in the root directory and add the following:

     ```
     HUGGING_FACE_API_KEY=your_hugging_face_api_key
     FLASK_SECRET_KEY=your_flask_secret_key
     ```

4. **Run the Flask App**:

   ```bash
   python app.py
   ```

5. **Access the Application**:
   - Open a browser and navigate to `http://127.0.0.1:5000`.

---

## **How It Works**

1. **Backend**:
   - The Flask backend processes voice commands using the Hugging Face zero-shot classification model.
   - Commands are matched against predefined actions or classified using AI.

2. **Frontend**:
   - The frontend dynamically updates the UI based on responses from the backend.
   - Speech recognition is handled using the browser's Web Speech API.

3. **Real-Time Communication**:
   - Flask-SocketIO enables real-time communication between the backend and frontend.

---

## **Technologies Used**

- **Backend**: Flask, Flask-SocketIO, Hugging Face API.
- **Frontend**: HTML, CSS, JavaScript.
- **Speech Recognition**: Browser's Web Speech API.
- **AI Model**: Hugging Face zero-shot classification (`typeform/distilbert-base-uncased-mnli`).

---

## **Commands Supported**

1. **Text Size**:
   - "Make text bigger."
   - "Make text smaller."
   - "Text too big."
   - "Text too small"

2. **Contrast**:
   - "Switch to dark mode."
   - "Switch to light mode."
   - "Too bright."
   - "Can't see."
   - "Text too dark."

3. **Time**:
   - "What time is it?"

4. **Identity**:
   - "Who am I?"
   - "What's my name?"
   - "Where am I?"


---

## **License**

This project is licensed under the MIT License.

---

