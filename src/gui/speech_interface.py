import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import speech_recognition as sr
import pyttsx3

from src.core.nlu import find_dish_in_text
from src.core.knowledge import get_recipe
from core.themealdb_api import query_huggingface
from src.core.custom_llm import generate_recipe_from_ingredients
from src.gui.mode_selection_ui import run_mode_selection_ui

def run_speech_interface(mode):
    engine = pyttsx3.init()
    listening = False
    listen_thread = None

    def recognize_speech():
        nonlocal listening
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        try:
            with mic as source:
                status_label.config(text="Listening...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            status_label.config(text="Recognizing...")
            text = recognizer.recognize_google(audio)
            recognized_text_var.set(text)
            add_chat_message("You", text)

            if mode == "existing_recipe":
                dish = find_dish_in_text(text)
                if dish:
                    response = get_recipe(dish)
                else:
                    response = "Sorry, I couldn't find a matching recipe."
            elif mode == "huggingface":
                response = query_huggingface(text)
            elif mode == "custom_model":
                response = generate_recipe_from_ingredients(text)
            else:
                response = f"[Mode: {mode}] Echo: {text}"

            add_chat_message("Bot", response)
            speak_button.config(state=tk.NORMAL)
            speak_button.last_reply = response
        except sr.WaitTimeoutError:
            messagebox.showerror("Error", "Listening timed out, please try again.")
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Could not understand audio")
        except sr.RequestError as e:
            messagebox.showerror("Error", f"Could not request results; {e}")
        finally:
            status_label.config(text="")
            toggle_listen(False)

    def on_mic_click():
        nonlocal listening, listen_thread
        if not listening:
            toggle_listen(True)
            listen_thread = threading.Thread(target=recognize_speech, daemon=True)
            listen_thread.start()
        else:
            # Stopping listening is tricky with speech_recognition; here we just toggle UI
            toggle_listen(False)

    def toggle_listen(state):
        nonlocal listening
        listening = state
        if listening:
            mic_button.config(text="🛑 Stop")
        else:
            mic_button.config(text="🎤 Start")

    def add_chat_message(sender, message):
        chat_area.config(state='normal')
        tag = "user" if sender == "You" else "bot"
        chat_area.insert(tk.END, f"{sender}: {message}\n", tag)
        chat_area.config(state='disabled')
        chat_area.yview(tk.END)

    def on_speak():
        text = getattr(speak_button, 'last_reply', None)
        if text:
            engine.say(text)
            engine.runAndWait()

    def on_back():
        window.destroy()
        run_mode_selection_ui()

    window = tk.Tk()
    window.title(f"Recipe ChatBot - Speech Interface ({mode.replace('_', ' ').title()})")
    window.geometry("700x500")
    window.minsize(700, 500)
    window.maxsize(700, 500)

    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=0)

    chat_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Arial", 12))
    chat_area.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="nsew")
    chat_area.config(state='disabled')

    # Define tags for coloring and spacing
    chat_area.tag_config("user", foreground="blue")
    chat_area.tag_config("bot", foreground="green")
    chat_area.tag_config("bot", foreground="green", spacing3=10)
    
    recognized_text_var = tk.StringVar()
    recognized_label = tk.Label(window, textvariable=recognized_text_var, font=("Arial", 14), fg="blue")
    recognized_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))

    status_label = tk.Label(window, text="", font=("Arial", 10), fg="green")
    status_label.grid(row=2, column=0, columnspan=2, pady=(0, 10))

    button_frame = tk.Frame(window)
    button_frame.grid(row=3, column=0, columnspan=2, pady=10)

    mic_button = tk.Button(button_frame, text="🎤 Start", font=("Arial", 20), width=8, command=on_mic_click)
    mic_button.pack(side=tk.LEFT, padx=10)

    speak_button = tk.Button(button_frame, text="Speak", font=("Arial", 20), width=8, command=on_speak, state=tk.DISABLED)
    speak_button.pack(side=tk.LEFT, padx=10)

    back_btn = tk.Button(button_frame, text="Back", font=("Arial", 12, "bold"), command=on_back)
    back_btn.pack(side=tk.LEFT, padx=8)

    window.mainloop()

if __name__ == "__main__":
    run_speech_interface("existing_recipe")