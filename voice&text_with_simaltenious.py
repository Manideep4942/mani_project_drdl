import os
import tkinter as tk
from tkinter import messagebox
import pyttsx3
import mysql.connector
import pyaudio
import json
from vosk import Model, KaldiRecognizer
import threading

# Function to initialize text-to-speech engine
def init_text_to_speech():
    engine = pyttsx3.init()
    return engine

# Function to initialize Vosk speech recognition model
def init_speech_recognition(model_path):
    if not os.path.exists(model_path):
        print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
        exit(1)
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)
    return recognizer

# Function to recognize speech input
def recognize_speech(recognizer):
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    print("Listening...")
    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            query = result.get('text', '')
            if query:
                print("User Query:", query)
                return query
        elif recognizer.PartialResult():
            partial_result = json.loads(recognizer.PartialResult())
            if partial_result.get('partial'):
                print("Partial Query:", partial_result['partial'])

# Function to query the database
def query_database(query):
    # Connect to MySQL database
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mani",
        database="drdl"
    )

    cursor = connection.cursor()
    # Execute the query
    cursor.execute("SELECT answer FROM faq WHERE question LIKE %s", (f"%{query}%",))
    
    # Fetch all results
    result = cursor.fetchall()
    cursor.close()
    connection.close()

    # If there are results, return the first one
    if result:
        return result[0]
    else:
        return None

# Function to speak the response
def speak_response(response, engine):
    engine.say(response)
    engine.runAndWait()

# Function to handle text input
def handle_text_input():
    query = text_entry.get()
    if query:
        result = query_database(query)
        if result:
            result_label.config(text=result[0])
            threading.Thread(target=speak_response, args=(result[0], engine)).start()
        else:
            result_label.config(text="Sorry, I couldn't find an answer to your question in the database.")
    else:
        messagebox.showerror("Error", "Please enter a question.")

# Function to handle voice input
def handle_voice_input():
    threading.Thread(target=handle_voice_response).start()

# Function to handle voice response
def handle_voice_response():
    query = recognize_speech(recognizer)
    if query:
        result = query_database(query)
        if result:
            result_label.config(text=result[0])
            speak_response(result[0], engine)
        else:
            result_label.config(text="Sorry, I couldn't find an answer to your question in the database.")

# Initialize GUI
root = tk.Tk()
root.title("DRDL Question Bank")
root.geometry("1200x600")
root.configure(bg="#f0f0f0")

# Create frame
frame = tk.Frame(root, bg="#f0f0f0")
frame.pack(pady=20)

# Create labels
text_label = tk.Label(frame, text="Enter your question:", font=("Arial", 12), bg="#f0f0f0")
text_label.grid(row=0, column=0, padx=10, pady=10)

# Create text entry
text_entry = tk.Entry(frame, width=50, font=("Arial", 12))
text_entry.grid(row=0, column=1, padx=10, pady=10)

# Create buttons
text_button = tk.Button(frame, text="Ask (Text)", command=handle_text_input, font=("Arial", 12), bg="#4CAF50", fg="white")
text_button.grid(row=1, column=0, columnspan=2, pady=10, padx=5, sticky="ew")

voice_button = tk.Button(frame, text="Ask (Voice)", command=handle_voice_input, font=("Arial", 12), bg="#2196F3", fg="white")
voice_button.grid(row=2, column=0, columnspan=2, pady=10, padx=5, sticky="ew")

# Create label for displaying result
result_label = tk.Label(root, text="", font=("Arial", 14), wraplength=500, justify="center", bg="#f0f0f0")
result_label.pack(pady=20)

# Initialize speech recognition and text-to-speech engines
recognizer = init_speech_recognition("C:/Users/manid/OneDrive/Desktop/drdl/vosk-model-small-en-us-0.15")  # Replace with the actual path to the Vosk model directory
engine = init_text_to_speech()

root.mainloop()
