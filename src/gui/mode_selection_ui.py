import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import tkinter as tk
from src.gui import input_type_ui  # Next UI to select input type

class ModeSelectionUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Recipe ChatBot - Select Mode")
        self.root.geometry("400x300")
        
        tk.Label(root, text="Select Mode:", font=("Arial", 16, "bold")).pack(pady=20)
        
        self.mode_var = tk.StringVar(value="existing_recipe")
        
        modes = [
            ("Existing Recipe", "existing_recipe"),
            ("Use huggingface Token", "huggingface"),
            ("Hugging Face Model", "custom_model"),
            ("Task 2 Model", "task2"),
        ]
        
        for text, mode in modes:
            tk.Radiobutton(root, text=text, variable=self.mode_var, value=mode, font=("Arial", 12)).pack(anchor="w", padx=40, pady=5)
        
        tk.Button(root, text="Next", font=("Arial", 12, "bold"), command=self.go_to_input_type).pack(pady=30)
    
    def go_to_input_type(self):
        selected_mode = self.mode_var.get()
        self.root.destroy()  # Close current window
        input_type_ui.run_input_type_ui(selected_mode)  # Pass mode to next UI

def run_mode_selection_ui():
    root = tk.Tk()
    app = ModeSelectionUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_mode_selection_ui()