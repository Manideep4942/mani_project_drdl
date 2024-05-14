import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr
import pyttsx3
import mysql.connector

# Function to initialize text-to-speech engine
def init_text_to_speech():
    engine = pyttsx3.init()
    
    # List all available voices
    voices = engine.getProperty('voices')
    for voice in voices:
        if "female" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    else:
        print("No female voice found, using default voice.")

    return engine

# Function to initialize speech recognition engine
def init_speech_recognition():
    recognizer = sr.Recognizer()
    return recognizer

# Function to recognize speech input
def recognize_speech(recognizer):
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio)
        print("User Query:", query)
        return query
    except sr.UnknownValueError:
        print("Sorry, I didn't get that.")
        return None
    except sr.RequestError:
        print("Sorry, I'm facing some technical issue. Please try again later.")
        return None

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
            speak_response(result[0], engine)
            result_label.config(text=result[0])
        else:
            result_label.config(text="Sorry, I couldn't find an answer to your question in the database.")
    else:
        messagebox.showerror("Error", "Please enter a question.")

# Function to handle voice input
def handle_voice_input():
    query = recognize_speech(recognizer)
    if query:
        print(f"Recognized query: {query}")  # Debugging print
        text_entry.delete(0, tk.END)
        text_entry.insert(0, query)
        result = query_database(query)
        if result:
            speak_response(result[0], engine)
            result_label.config(text=result[0])
        else:
            result_label.config(text="Sorry, I couldn't find an answer to your question in the database.")
    else:
        result_label.config(text="Sorry, I didn't get that.")

# Initialize GUI
root = tk.Tk()
root.title("Q&A System")
root.geometry("600x400")

# Create frame
frame = tk.Frame(root)
frame.pack(pady=20)

# Create labels
text_label = tk.Label(frame, text="Enter your question:", font=("Arial", 12))
text_label.grid(row=0, column=0, padx=10)

# Create text entry
text_entry = tk.Entry(frame, width=50, font=("Arial", 12))
text_entry.grid(row=0, column=1, padx=10)

# Create buttons
text_button = tk.Button(frame, text="Ask (Text)", command=handle_text_input, font=("Arial", 12))
text_button.grid(row=1, column=0, columnspan=2, pady=10)

voice_button = tk.Button(frame, text="Ask (Voice)", command=handle_voice_input, font=("Arial", 12))
voice_button.grid(row=2, column=0, columnspan=2, pady=10)

# Create label for displaying result
result_label = tk.Label(root, text="", font=("Arial", 14), wraplength=500, justify="center")
result_label.pack(pady=20)

# Initialize speech recognition and text-to-speech engines
recognizer = init_speech_recognition()
engine = init_text_to_speech()

root.mainloop()
