import os
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import pyttsx3
import mysql.connector
import threading
from difflib import SequenceMatcher
from vosk import Model, KaldiRecognizer
import pyaudio
import json


# Function to initialize text-to-speech engine
def init_text_to_speech():
    engine = pyttsx3.init()
    return engine


# Function to initialize Vosk speech recognition model
def init_speech_recognition(model_path):
    if not os.path.exists(model_path):
        print(
            "Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
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
    cursor.execute("SELECT question, answer FROM faq")

    # Fetch all results
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    # Find the most similar question and return its answer
    max_similarity = 0
    related_answer = None
    for question, answer in results:
        similarity = SequenceMatcher(None, query.lower(), question.lower()).ratio()
        if similarity > max_similarity:
            max_similarity = similarity
            related_answer = answer

    return related_answer


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
            result_label.config(text=result)
            threading.Thread(target=speak_response, args=(result, engine)).start()
        else:
            result_label.config(text="Sorry, I couldn't find an answer to your question or a related one.")
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
            result_label.config(text=result)
            speak_response(result, engine)
        else:
            result_label.config(text="Sorry, I couldn't find an answer to your question or a related one.")


# Function to handle admin login
def admin_login():
    password = simpledialog.askstring("Admin Login", "Enter Admin Password:", show='*')
    # Replace 'admin_password' with your actual admin password
    if password == 'manideep':
        admin_panel()
    else:
        messagebox.showerror("Login Failed", "Invalid Password")


# Function to display admin panel
def admin_panel():
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Panel")

    # Function to handle insert button click
    def insert_data():
        question = question_entry.get().strip()
        answer = answer_entry.get("1.0", tk.END).strip()
        if question and answer:
            # Insert data into database
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="mani",
                database="drdl"
            )
            cursor = connection.cursor()
            insert_query = "INSERT INTO faq (question, answer) VALUES (%s, %s)"
            insert_values = (question, answer)
            cursor.execute(insert_query, insert_values)
            connection.commit()
            cursor.close()
            connection.close()
            messagebox.showinfo("Success", "Data inserted successfully!")
            # Clear entry fields after insertion
            question_entry.delete(0, tk.END)
            answer_entry.delete("1.0", tk.END)
        else:
            messagebox.showerror("Error", "Please enter both question and answer.")

    # Function to handle update button click
    def update_data():
        def search_data():
            question_id = id_entry.get().strip()
            question_text = question_entry.get().strip()

            if question_id or question_text:
                # Connect to MySQL database
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="mani",
                    database="drdl"
                )
                cursor = connection.cursor()

                if question_id:
                    cursor.execute("SELECT id, question, answer FROM faq WHERE id = %s", (question_id,))
                else:
                    cursor.execute("SELECT id, question, answer FROM faq WHERE question = %s", (question_text,))

                result = cursor.fetchone()
                cursor.close()
                connection.close()

                if result:
                    id_entry.delete(0, tk.END)
                    id_entry.insert(0, result[0])
                    question_entry.delete(0, tk.END)
                    question_entry.insert(0, result[1])
                    answer_entry.delete("1.0", tk.END)
                    answer_entry.insert(tk.END, result[2])
                else:
                    messagebox.showerror("Error", "Question not found!")

        def update_question():
            question_id = id_entry.get().strip()
            question = question_entry.get().strip()
            answer = answer_entry.get("1.0", tk.END).strip()
            if question_id and question and answer:
                # Connect to MySQL database
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="mani",
                    database="drdl"
                )
                cursor = connection.cursor()
                # Execute the query to update question and answer
                cursor.execute("UPDATE faq SET question = %s, answer = %s WHERE id = %s",
                               (question, answer, question_id))
                connection.commit()
                cursor.close()
                connection.close()
                messagebox.showinfo("Success", "Question and answer updated successfully!")
            else:
                messagebox.showerror("Error", "Please enter ID, question, and answer.")

        def go_back():
            update_window.destroy()

        # Create update window
        update_window = tk.Toplevel(admin_window)
        update_window.title("Update Question")

        # Create labels and entry boxes
        id_label = tk.Label(update_window, text="ID:", font=("Arial", 12))
        id_label.grid(row=0, column=0, padx=10, pady=10)
        id_entry = tk.Entry(update_window, font=("Arial", 12), width=50)
        id_entry.grid(row=0, column=1, padx=10, pady=10)

        question_label = tk.Label(update_window, text="Question:", font=("Arial", 12))
        question_label.grid(row=1, column=0, padx=10, pady=10)
        question_entry = tk.Entry(update_window, font=("Arial", 12), width=50)
        question_entry.grid(row=1, column=1, padx=10, pady=10)

        answer_label = tk.Label(update_window, text="Answer:", font=("Arial", 12))
        answer_label.grid(row=2, column=0, padx=10, pady=10)
        answer_entry = tk.Text(update_window, font=("Arial", 12), width=50, height=5)
        answer_entry.grid(row=2, column=1, padx=10, pady=10)

        # Create buttons
        search_button = tk.Button(update_window, text="Search", command=search_data, font=("Arial", 12), bg="#006400",
                                  fg="white")
        search_button.grid(row=3, column=0, padx=5, pady=10)

        update_button = tk.Button(update_window, text="Update Data", command=update_question, font=("Arial", 12),
                                  bg="#006400", fg="white")
        update_button.grid(row=3, column=1, padx=5, pady=10)

        back_button = tk.Button(update_window, text="Back", command=go_back, font=("Arial", 12), bg="#929591",
                                fg="white")
        back_button.grid(row=3, column=3, columnspan=2, padx=5, pady=10)

    # Function to handle delete button click
    def delete_data():
        # Create delete window
        delete_window = tk.Toplevel(admin_window)
        delete_window.title("Delete Question")

        # Function to search question by ID
        def search_by_id():
            question_id = id_entry.get().strip()
            if question_id:
                # Connect to MySQL database
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="mani",
                    database="drdl"
                )
                cursor = connection.cursor()
                # Execute the query to fetch the question details
                cursor.execute("SELECT id, question, answer FROM faq WHERE id = %s", (question_id,))
                question_details = cursor.fetchone()
                cursor.close()
                connection.close()
                if question_details:
                    # Display the question details to the admin
                    show_question_details(question_details)

                    # Function to confirm deletion
                    def confirm_delete():
                        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this question?"):
                            delete_question(question_details[0])  # Pass the question ID for deletion
                            delete_window.destroy()

                    confirm_button = tk.Button(delete_window, text="Confirm Delete", command=confirm_delete,
                                               font=("Arial", 12), bg="#FF5733", fg="white")
                    confirm_button.grid(row=5, column=0, columnspan=2, padx=5, pady=10)
                else:
                    messagebox.showerror("Error", "Question not found!")
            else:
                messagebox.showerror("Error", "Please enter the question ID.")

        # Function to search question by text
        def search_by_text():
            question_text = question_entry.get().strip()
            if question_text:
                # Connect to MySQL database
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="mani",
                    database="drdl"
                )
                cursor = connection.cursor()
                # Execute the query to fetch the question details
                cursor.execute("SELECT id, question, answer FROM faq WHERE question = %s", (question_text,))
                question_details = cursor.fetchone()
                cursor.close()
                connection.close()
                if question_details:
                    # Display the question details to the admin
                    show_question_details(question_details)

                    # Function to confirm deletion
                    def confirm_delete():
                        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this question?"):
                            delete_question(question_details[0])  # Pass the question ID for deletion
                            delete_window.destroy()

                    confirm_button = tk.Button(delete_window, text="Confirm Delete", command=confirm_delete,
                                               font=("Arial", 12), bg="#FF5733", fg="white")
                    confirm_button.grid(row=5, column=0, columnspan=2, padx=5, pady=10)
                else:
                    messagebox.showerror("Error", "Question not found!")
            else:
                messagebox.showerror("Error", "Please enter the question text.")

        # Function to delete question
        def delete_question(question_id):
            # Connect to MySQL database
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="mani",
                database="drdl"
            )
            cursor = connection.cursor()
            # Execute the query to delete the question
            cursor.execute("DELETE FROM faq WHERE id = %s", (question_id,))
            connection.commit()
            cursor.close()
            connection.close()
            messagebox.showinfo("Success", "Question deleted successfully!")

        # Function to display question details
        def show_question_details(question_details):
            id_label = tk.Label(delete_window, text="ID:", font=("Arial", 12))
            id_label.grid(row=8, column=0, padx=10, pady=10)
            id_value_label = tk.Label(delete_window, text=question_details[0], font=("Arial", 12))
            id_value_label.grid(row=8, column=1, padx=10, pady=10)

            question_label = tk.Label(delete_window, text="Question:", font=("Arial", 12))
            question_label.grid(row=9, column=0, padx=10, pady=10)
            question_value_label = tk.Label(delete_window, text=question_details[1], font=("Arial", 12))
            question_value_label.grid(row=9, column=1, padx=10, pady=10)

            answer_label = tk.Label(delete_window, text="Answer:", font=("Arial", 12))
            answer_label.grid(row=10, column=0, padx=10, pady=10)
            answer_text = tk.Text(delete_window, font=("Arial", 12), width=80, height=7)
            answer_text.grid(row=10, column=1, padx=10, pady=10)
            answer_text.insert(tk.END, question_details[2])
            answer_text.config(state=tk.DISABLED)  # Prevent editing

        # Create labels and entry boxes
        id_label = tk.Label(delete_window, text="ID:", font=("Arial", 12))
        id_label.grid(row=0, column=0, padx=10, pady=10)
        id_entry = tk.Entry(delete_window, font=("Arial", 12), width=50)
        id_entry.grid(row=0, column=1, padx=10, pady=10)

        question_label = tk.Label(delete_window, text="Question:", font=("Arial", 12))
        question_label.grid(row=2, column=0, padx=10, pady=10)
        question_entry = tk.Entry(delete_window, font=("Arial", 12), width=50)
        question_entry.grid(row=2, column=1, padx=10, pady=10)

        # Create buttons for search by ID and search by question text
        search_button_id = tk.Button(delete_window, text="Search by ID", command=search_by_id, font=("Arial", 12),
                                     bg="#006400", fg="white")
        search_button_id.grid(row=1, column=0, padx=5, pady=10)

        search_button_text = tk.Button(delete_window, text="Search by Question Text", command=search_by_text,
                                       font=("Arial", 12), bg="#006400", fg="white")
        search_button_text.grid(row=3, column=0, padx=5, pady=10)

        # Function to close the delete window and go back to admin panel
        def go_back():
            delete_window.destroy()

        back_button = tk.Button(delete_window, text="Back", command=go_back, font=("Arial", 12), bg="#929591",
                                fg="white")
        back_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

    # Create labels and entry boxes for insert
    question_label = tk.Label(admin_window, text="Question:", font=("TimesNewRoman", 12))
    question_label.grid(row=0, column=0, padx=10, pady=10)
    question_entry = tk.Entry(admin_window, font=("Arial", 12), width=70)
    question_entry.grid(row=0, column=1, padx=10, pady=10)

    answer_label = tk.Label(admin_window, text="Answer:", font=("TimesNewRoman", 12))
    answer_label.grid(row=1, column=0, padx=10, pady=10)
    answer_entry = tk.Text(admin_window, font=("Arial", 12), width=70, height=8)
    answer_entry.grid(row=1, column=1, padx=10, pady=10)

    # Create buttons for insert, update, delete, and logout in a single row
    insert_button = tk.Button(admin_window, text="Insert Data", command=insert_data, font=("Arial", 12), bg="#2196F3",
                              fg="white")
    insert_button.grid(row=3, column=0, padx=5, pady=10)

    update_button = tk.Button(admin_window, text="Update", command=update_data, font=("Arial", 12), bg="#2196F3",
                              fg="white")
    update_button.grid(row=3, column=1, padx=5, pady=10)

    delete_button = tk.Button(admin_window, text="Delete", command=delete_data, font=("Arial", 12), bg="#2196F3",
                              fg="white")
    delete_button.grid(row=3, column=2, padx=5, pady=10)

    logout_button = tk.Button(admin_window, text="Logout", command=admin_window.destroy, font=("Arial", 12),
                              bg="#FE420F", fg="white")
    logout_button.grid(row=8, column=1, padx=5, pady=10)


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
options = ["what is Astra?", "What is a database", "What is python", "What is a laptop?"]
text_entry = ttk.Combobox(frame, values=options, width=50, font=("Arial", 12))
text_entry.grid(row=0, column=1, padx=10, pady=10)

# Create buttons
text_button = tk.Button(frame, text="Ask (Text)", command=handle_text_input, font=("Arial", 12), bg="#4CAF50", fg="white",width=10)
text_button.grid(row=1, column=0, padx=5, pady=10, sticky="ew")

voice_button = tk.Button(frame, text="Ask (Voice)", command=handle_voice_input, font=("Arial", 12), bg="#2196F3", fg="white",width=10)
voice_button.grid(row=2, column=0, padx=5, pady=10, sticky="ew")

admin_button = tk.Button(frame, text="Admin Login", command=admin_login, font=("Arial", 12), bg="#FE420F", fg="white",width=10)
admin_button.grid(row=0, column=3, padx=5, pady=10, sticky="ew")

# Create label for displaying result
result_label = tk.Label(root, text="", font=("TimesNewRoman", 15), wraplength=800, justify="center", bg="#f0f0f0")
result_label.pack(pady=20, fill=tk.X)


# Initialize speech recognition and text-to-speech engines
recognizer = init_speech_recognition("C:/Users/manid/OneDrive/Desktop/drdl/vosk-model-small-en-us-0.15")  # Replace with the actual path to the Vosk model directory
engine = init_text_to_speech()

root.mainloop()
