import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import tkinter as tk
from src.gui import text_interface, speech_interface

def run_input_type_ui(selected_mode):
    def open_text():
        window.destroy()
        text_interface.run_text_interface(selected_mode)
    
    def open_speech():
        window.destroy()
        speech_interface.run_speech_interface(selected_mode)
    
    window = tk.Tk()
    window.title("Recipe ChatBot - Select Input Type")
    window.geometry("400x250")
    
    tk.Label(window, text=f"Mode: {selected_mode.replace('_', ' ').title()}", font=("Arial", 14)).pack(pady=20)
    tk.Label(window, text="Choose input method:", font=("Arial", 12)).pack(pady=10)
    
    tk.Button(window, text="Text", font=("Arial", 14), width=15, command=open_text).pack(pady=10)
    tk.Button(window, text="Speech", font=("Arial", 14), width=15, command=open_speech).pack(pady=10)
    
    window.mainloop()