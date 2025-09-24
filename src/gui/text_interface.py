import tkinter as tk
from tkinter import scrolledtext
import pyttsx3

from src.core.nlu import find_dish_in_text
from src.core.knowledge import get_recipe
from src.core.huggingface_api import query_huggingface
from src.core.custom_llm import generate_recipe_from_ingredients
from src.gui.mode_selection_ui import run_mode_selection_ui

def run_text_interface(mode):
    engine = pyttsx3.init()
    
    def on_submit():
        user_input = input_text.get("1.0", tk.END).strip()
        if not user_input:
            return
        input_text.delete("1.0", tk.END)
        
        chat_area.config(state='normal')
        chat_area.insert(tk.END, f"You: {user_input}\n", "user")
        chat_area.config(state='disabled')
        
        if mode == "existing_recipe":
            dish = find_dish_in_text(user_input)
            if dish:
                response = get_recipe(dish)
            else:
                response = "Sorry, I couldn't find a matching recipe."
        elif mode == "huggingface":
            response = query_huggingface(user_input)
        elif mode == "custom_model":
            response = generate_recipe_from_ingredients(user_input)
        else:
            response = f"[Mode: {mode}] Echo: {user_input}"
        
        chat_area.config(state='normal')
        chat_area.insert(tk.END, f"Bot: {response}\n", "bot")
        chat_area.config(state='disabled')
        chat_area.yview(tk.END)
        
        # Enable speak button after bot reply
        speak_button.config(state=tk.NORMAL)
        # Store last bot reply for speaking
        speak_button.last_reply = response

    def on_speak():
        text = getattr(speak_button, 'last_reply', None)
        if text:
            engine.say(text)
            engine.runAndWait()
    
    def on_back():
        window.destroy()
        run_mode_selection_ui()

    window = tk.Tk()
    window.title(f"Recipe ChatBot - Text Interface ({mode.replace('_', ' ').title()})")
    window.geometry("700x500")
    window.minsize(700, 500)
    window.maxsize(700, 500)  # Fix window size
    
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=0)
    
    chat_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Arial", 12))
    chat_area.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="nsew")
    chat_area.config(state='disabled')
    
    # Define tags for coloring
    chat_area.tag_config("user", foreground="blue")
    chat_area.tag_config("bot", foreground="green", spacing3=10)
    
    input_text = tk.Text(window, height=5, font=("Arial", 14))
    input_text.grid(row=1, column=0, padx=(10, 5), pady=(5, 10), sticky="nsew")
    input_text.focus()
    
    button_frame = tk.Frame(window)
    button_frame.grid(row=1, column=1, padx=(5, 10), pady=(5, 10), sticky="ns")
    
    submit_button = tk.Button(button_frame, text="Enter", font=("Arial", 12, "bold"), command=on_submit)
    submit_button.pack(fill=tk.X, pady=(0, 10))
    
    speak_button = tk.Button(button_frame, text="Speak", font=("Arial", 12, "bold"), command=on_speak, state=tk.DISABLED)
    speak_button.pack(fill=tk.X)

    back_btn = tk.Button(button_frame, text="Back", font=("Arial", 12, "bold"), command=on_back)
    back_btn.pack(side=tk.LEFT, padx=8)
    
    window.mainloop()

if __name__ == "__main__":
    run_text_interface("existing_recipe")