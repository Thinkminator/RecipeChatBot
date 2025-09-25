
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from .base_page import BasePage
from backend import generate_bot_reply, speak_text

try:
    import speech_recognition as sr
except Exception:
    sr = None

class SpeechPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.title_var.set("Speech Interface")

        self.chat = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Segoe UI", 12))
        self.chat.pack(fill="both", expand=True, padx=10, pady=(0, 6))
        self.chat.tag_config("user", foreground="blue")
        self.chat.tag_config("bot", foreground="green", spacing3=8)
        self.chat.config(state="disabled")

        self.heard_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self.heard_var, font=("Segoe UI", 11), foreground="blue")\
            .pack(pady=(0, 6))

        self.status_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self.status_var, font=("Segoe UI", 9))\
            .pack(pady=(0, 8))

        row = ttk.Frame(self)
        row.pack(pady=(0, 10))
        self.toggle_btn = ttk.Button(row, text="🎤 Start", command=self.on_toggle_listen)
        self.toggle_btn.pack(side="left", padx=8)
        self.speak_btn = ttk.Button(row, text="Speak", command=self.on_speak, state="disabled")
        self.speak_btn.pack(side="left", padx=8)

        self._listening = False
        self._last_reply = None

    def on_show(self, **_):
        mode = self.app.state.get("mode") or "—"
        self.title_var.set(f"Speech Interface — {mode.replace('_', ' ').title()}")
        self.set_back_enabled(True)

    def on_hide(self):
        if self._listening:
            self._listening = False
            self.toggle_btn.config(text="🎤 Start")
            self.status_var.set("Stopped listening.")

    def add_msg(self, who, text, tag):
        self.chat.config(state="normal")
        self.chat.insert(tk.END, f"{who}: {text}\n", tag)
        self.chat.config(state="disabled")
        self.chat.yview(tk.END)

    def on_toggle_listen(self):
        if not sr:
            messagebox.showwarning("Speech not available", "speech_recognition not installed.")
            return
        self._listening = not self._listening
        self.toggle_btn.config(text="🛑 Stop" if self._listening else "🎤 Start")
        if self._listening:
            self.status_var.set("Listening… Speak now.")
            self.after(100, self.listen_once)
        else:
            self.status_var.set("Stopped listening.")

    def listen_once(self):
        if not self._listening or not sr:
            return
        r = sr.Recognizer()
        with sr.Microphone() as mic:
            try:
                r.adjust_for_ambient_noise(mic, duration=0.5)
                self.status_var.set("Listening…")
                audio = r.listen(mic, timeout=5, phrase_time_limit=8)
                self.status_var.set("Recognizing…")
                text = r.recognize_google(audio)
            except sr.WaitTimeoutError:
                self.status_var.set("Timeout—no speech detected.")
                if self._listening:
                    self.after(400, self.listen_once)
                return
            except sr.UnknownValueError:
                self.status_var.set("Could not understand audio.")
                if self._listening:
                    self.after(400, self.listen_once)
                return
            except Exception as e:
                messagebox.showerror("Speech Error", str(e))
                self._listening = False
                self.toggle_btn.config(text="🎤 Start")
                return

        self.heard_var.set(text)
        self.add_msg("You", text, "user")

        reply = generate_bot_reply(self.app.state.get("mode"), text)
        self.add_msg("Bot", reply, "bot")
        self._last_reply = reply
        self.speak_btn.state(["!disabled"])

        if self._listening:
            self.after(400, self.listen_once)

    def on_speak(self):
        if self._last_reply:
            ok = speak_text(self._last_reply)
            if not ok:
                messagebox.showwarning("TTS not available", "pyttsx3 not installed.")
