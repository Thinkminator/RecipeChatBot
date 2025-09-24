# src/gui/image_interface.py
# Tkinter UI that allows the user to pick an image, displays it inline in chat, runs a VLM
# to guess a dish name / caption, builds the prompt "How to cook [caption]?" and passes it
# to the correct generation pipeline based on the selected mode.

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
from PIL import Image, ImageTk
import os

# Core functions (lazy imports inside handlers where needed)
from src.core.vlm import infer_dish_from_image
from src.gui.mode_selection_ui import run_mode_selection_ui


def run_image_interface(mode):
    engine = None
    try:
        import pyttsx3
        engine = pyttsx3.init()
    except Exception:
        engine = None

    window = tk.Tk()
    window.title(f"Recipe ChatBot - Image Interface ({mode.replace('_', ' ').title()})")
    window.geometry("800x600")
    window.minsize(800, 600)

    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=0)

    chat_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Arial", 12))
    chat_area.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="nsew")
    chat_area.config(state='disabled')

    # Tag styles
    chat_area.tag_config("user", foreground="blue")
    chat_area.tag_config("bot", foreground="green", spacing3=10)

    # We will keep references to PhotoImage objects so they are not garbage-collected
    image_refs = []

    # File path of selected image
    selected_image_path_var = tk.StringVar(value="")

    # Display small label for selected file
    selected_label = tk.Label(window, textvariable=selected_image_path_var, anchor="w", font=("Arial", 10))
    selected_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=10)

    # Buttons frame
    button_frame = tk.Frame(window)
    button_frame.grid(row=2, column=0, columnspan=2, pady=10)

    def open_image():
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")]
        )
        if not file_path:
            return
        selected_image_path_var.set(file_path)

    def insert_image_in_chat(image_path, from_user=True):
        """Insert image into the chat area and keep reference to PhotoImage."""
        try:
            pil_img = Image.open(image_path)
            # Resize to reasonable width for chat area while preserving aspect ratio
            max_width = 400
            if pil_img.width > max_width:
                ratio = max_width / pil_img.width
                new_size = (max_width, int(pil_img.height * ratio))
                pil_img = pil_img.resize(new_size, Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil_img)
            image_refs.append(tk_img)  # keep reference
            chat_area.config(state="normal")
            if from_user:
                chat_area.insert(tk.END, "You: \n", "user")
            # Insert the image
            chat_area.image_create(tk.END, image=tk_img)
            chat_area.insert(tk.END, "\n", "user")
            chat_area.config(state="disabled")
            chat_area.yview(tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Could not display image: {e}")

    def on_enter():
        image_path = selected_image_path_var.get()
        if not image_path or not os.path.exists(image_path):
            messagebox.showwarning("No image", "Please select an image first.")
            return

        # Display the user image in chat immediately
        insert_image_in_chat(image_path, from_user=True)

        # Disable buttons while processing
        open_btn.config(state=tk.DISABLED)
        enter_btn.config(state=tk.DISABLED)
        back_btn.config(state=tk.DISABLED)
        speak_btn.config(state=tk.DISABLED)

        # Run VLM and generation in a background thread
        def worker():
            try:
                # 1) Infer caption/dish from image
                caption = infer_dish_from_image(image_path)
                if not caption:
                    caption = "an unknown dish"
                # 2) Build prompt and send to your text pipeline
                prompt = f"How to cook {caption}?"

                # 3) Route to correct handler based on mode
                if mode == "existing_recipe":
                    from src.core.nlu import find_dish_in_text
                    from src.core.knowledge import get_recipe
                    dish = find_dish_in_text(prompt)
                    if dish:
                        response = get_recipe(dish)
                    else:
                        response = "Sorry, I couldn't find a matching recipe."
                elif mode == "huggingface":
                    from src.core.huggingface_api import query_huggingface
                    response = query_huggingface(prompt)
                elif mode == "custom_model":
                    from src.core.custom_llm import generate_recipe_from_ingredients
                    response = generate_recipe_from_ingredients(prompt)
                else:
                    response = f"[Mode: {mode}] Echo: {prompt}"

                # Post response in chat (bot)
                chat_area.config(state='normal')
                chat_area.insert(tk.END, f"Bot (image understanding): I think this is: {caption}\n", "bot")
                chat_area.insert(tk.END, f"Bot: {response}\n", "bot")
                chat_area.config(state='disabled')
                chat_area.yview(tk.END)

                # Enable speak button and store last reply
                speak_btn.config(state=tk.NORMAL)
                speak_btn.last_reply = response

                pass

            except Exception as e:
                chat_area.config(state='normal')
                chat_area.insert(tk.END, f"Bot: Error processing image: {e}\n", "bot")
                chat_area.config(state='disabled')
                chat_area.yview(tk.END)
            finally:
                # Re-enable buttons
                open_btn.config(state=tk.NORMAL)
                enter_btn.config(state=tk.NORMAL)
                back_btn.config(state=tk.NORMAL)
                # speak_btn already enabled if response exists
        threading.Thread(target=worker, daemon=True).start()

    def on_speak():
        text = getattr(speak_btn, 'last_reply', None)
        if text and engine is not None:
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                messagebox.showerror("TTS Error", str(e))

    def on_back():
        window.destroy()
        run_mode_selection_ui()

    # UI buttons
    open_btn = tk.Button(button_frame, text="Choose Image", font=("Arial", 12), command=open_image)
    open_btn.pack(side=tk.LEFT, padx=8)

    enter_btn = tk.Button(button_frame, text="Enter", font=("Arial", 12, "bold"), command=on_enter)
    enter_btn.pack(side=tk.LEFT, padx=8)

    speak_btn = tk.Button(button_frame, text="Speak", font=("Arial", 12), command=on_speak, state=tk.DISABLED)
    speak_btn.pack(side=tk.LEFT, padx=8)

    back_btn = tk.Button(button_frame, text="Back", font=("Arial", 12, "bold"), command=on_back)
    back_btn.pack(side=tk.LEFT, padx=8)

    window.mainloop()


if __name__ == "__main__":
    # For testing, default to custom_model
    run_image_interface("custom_model")