import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from .base_page import BasePage
from backend import generate_bot_reply, speak_text
import os
from PIL import Image, ImageTk
import threading

class ImagePage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.title_var.set("Image Interface")

        row = ttk.Frame(self)
        row.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
        row.pack_propagate(False)
        row.configure(height=60)

        self.selected_image_label = ttk.Label(row, text="No image selected", anchor="w", font=("Segoe UI", 12))
        self.selected_image_label.pack(side="left", fill="both", expand=True)

        button_frame = ttk.Frame(row)
        button_frame.pack(side="right")

        self.choose_btn = ttk.Button(button_frame, text="📁 Choose", command=self.open_image)
        self.choose_btn.pack(side="left", padx=(0, 8), ipady=10)  # ipady increases height

        self.send_btn = ttk.Button(button_frame, text="➤ Send", command=self.on_send, state="disabled")
        self.send_btn.pack(side="left", padx=(0, 8))

        self.speak_btn = ttk.Button(button_frame, text="🔊 Speak", command=self.on_speak, state="disabled")
        self.speak_btn.pack(side="left")

        self.chat = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Segoe UI", 12))
        self.chat.pack(fill="both", expand=True, padx=10, pady=(10, 6))
        self.chat.tag_config("user", foreground="blue")
        self.chat.tag_config("bot", foreground="green", spacing3=8)
        self.chat.config(state="disabled")

        self.selected_image_path = None

        self.image_refs = []

        self.engine = None
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
        except Exception:
            self.engine = None

    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")]
        )
        if file_path:
            self.selected_image_path = file_path
            filename = os.path.basename(file_path)
            self.selected_image_label.config(text=filename)
            self.send_btn.config(state="normal")
        else:
            self.selected_image_path = None
            self.selected_image_label.config(text="No image selected")
            self.send_btn.config(state="disabled")

    def insert_image_in_chat(self, image_path):
        try:
            pil_img = Image.open(image_path)
            max_width = 400
            if pil_img.width > max_width:
                ratio = max_width / pil_img.width
                new_size = (max_width, int(pil_img.height * ratio))
                pil_img = pil_img.resize(new_size, Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil_img)
            self.image_refs.append(tk_img)
            self.chat.config(state="normal")
            self.chat.insert(tk.END, "You: \n", "user")
            self.chat.image_create(tk.END, image=tk_img)
            self.chat.insert(tk.END, "\n", "user")
            self.chat.config(state="disabled")
            self.chat.yview(tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Could not display image: {e}")

    def on_send(self):
        if not self.selected_image_path or not os.path.exists(self.selected_image_path):
            messagebox.showwarning("No image", "Please select an image first.")
            return

        self.insert_image_in_chat(self.selected_image_path)

        self.choose_btn.config(state="disabled")
        self.send_btn.config(state="disabled")
        self.speak_btn.config(state="disabled")

        def worker():
            try:
                from backend import infer_dish_from_image  # lazy import
                caption = infer_dish_from_image(self.selected_image_path)
                if not caption:
                    caption = "an unknown dish"

                prompt = f"How to cook {caption}?"

                response = generate_bot_reply(self.app.state.get("mode"), prompt)

                self.chat.config(state="normal")
                self.chat.insert(tk.END, f"Bot (image understanding): I think this is: {caption}\n", "bot")
                self.chat.insert(tk.END, f"Bot: {response}\n", "bot")
                self.chat.config(state="disabled")
                self.chat.yview(tk.END)

                self.speak_btn.config(state="normal")
                self.speak_btn.last_reply = response

            except Exception as e:
                self.chat.config(state="normal")
                self.chat.insert(tk.END, f"Bot: Error processing image: {e}\n", "bot")
                self.chat.config(state="disabled")
                self.chat.yview(tk.END)
            finally:
                self.choose_btn.config(state="normal")
                self.send_btn.config(state="normal")

        threading.Thread(target=worker, daemon=True).start()

    def on_speak(self):
        text = getattr(self.speak_btn, 'last_reply', None)
        if text and self.engine is not None:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                messagebox.showerror("TTS Error", str(e))

    def on_show(self, **_):
        mode = self.app.state.get("mode") or "—"
        self.title_var.set(f"Text Interface — {mode.replace('_', ' ').title()}")