from flask import Flask, render_template, request, jsonify
import pyttsx3
import speech_recognition as sr
import whisper
from bardapi import Bard

app = Flask(__name__, static_folder='static', template_folder='templates')

# Replace these with your actual Bard API tokens
token = 'YOUR_BARD_API_TOKEN'  # Replace with your actual Bard API token

# Initialize Bard API
bard = Bard(token=token)

# Initialize speech recognition
r = sr.Recognizer()

# Initialize Whisper models
tiny_model = whisper.load_model("tiny")
base_model = whisper.load_model("base")

# Initialize text-to-speech
engine = pyttsx3.init()
rate = engine.getProperty("rate")  # Get current speech rate
engine.setProperty("rate", rate - 50)  # Adjust speech rate (50 words per minute slower)

# Function to send prompt to Bard and get a response
def prompt_bard(prompt):
    response = bard.get_answer(prompt)
    return response["content"]

# Function to speak text using pyttsx3
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen for a prompt using speech recognition and Whisper
def listen_for_prompt():
    with sr.Microphone() as source:
        try:
            print("Speak your prompt to Bard.\n")
            audio = r.listen(source)
            with open("prompt.wav", "wb") as f:
                f.write(audio.get_wav_data())
            result = base_model.transcribe("prompt.wav")
            prompt_text = result["text"]
            print("Sending to Bard:", prompt_text, "\n")
            if len(prompt_text.strip()) == 0:
                return ""
            return prompt_text
        except Exception as e:
            print("Error transcribing audio:", e)
            return ""

# Flask route for the main page
@app.route("/")
def index():
    return render_template("index.html")  # Assuming you have an index.html template

# Flask route to handle text-based prompts (POST request)
@app.route("/ask", methods=["POST"])
def ask():
    prompt = request.form["prompt"]
    response = prompt_bard(prompt)
    return jsonify({"response": response})

# Flask route to handle speaking a prompt (POST request)
@app.route("/speak", methods=["POST"])
def speak_prompt():
    prompt = request.form["prompt"]
    speak(prompt)
    return jsonify({"status": "success"})

# Flask route to handle listening to a prompt (POST request)
@app.route("/listen", methods=["POST"])
def listen_prompt():
    prompt = listen_for_prompt()
    if prompt:
        response = prompt_bard(prompt)
        speak(response)
        return jsonify({"response": response})
    else:
        return jsonify({"response": "No prompt recorded."})

# Run the Flask app in debug mode
if __name__ == "__main__":
    app.run(debug=True)