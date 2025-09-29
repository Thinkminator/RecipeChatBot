import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from .base_page import BasePage
from backend import generate_bot_reply, speak_text
import pyttsx3
try:
    import speech_recognition as sr
except Exception:
    sr = None

class SpeechPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.clear_btn = ttk.Button(self.header, text="🧹 Clear", command=self.on_clear)
        self.clear_btn.pack(side="right")  # top-right of the header row
        self.title_var.set("Speech Interface")

        row = ttk.Frame(self)
        row.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
        row.pack_propagate(False)
        row.configure(height=60)

        side = ttk.Frame(row, width=110)
        side.pack(side="right", padx=(8, 0), fill="y")
        side.pack_propagate(False)

        self.toggle_btn = ttk.Button(side, text="🎤 Start", width=10, command=self.on_toggle_listen)
        self.toggle_btn.pack(fill="x", pady=(0, 4))

        self.speak_btn = ttk.Button(side, text="🔊 Speak", width=10, command=self.on_speak, state="disabled")
        self.speak_btn.pack(fill="x")

        self.heard_text = tk.Text(row, height=2, font=("Segoe UI", 12), width=50, state="disabled", bg="SystemButtonFace", relief="flat")      
        self.heard_text.pack(side="left", fill="both", expand=True)
        self.heard_text.tag_configure("blue_text", foreground="blue")
        self.heard_text.tag_configure("black_text", foreground="black")
        

        self.chat = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Segoe UI", 12))
        self.chat.pack(fill="both", expand=True, padx=10, pady=(10, 6))
        self.chat.tag_config("user", foreground="blue")
        self.chat.tag_config("bot", foreground="green", spacing3=8)
        self.chat.config(state="disabled")

        self.speaking =False
        self._listening = False
        self._last_reply = None

    def on_show(self, **_):
        mode = self.app.state.get("mode") or "—"
        self.title_var.set(f"Speech Interface — {mode.replace('_', ' ').title()}")
        self.heard_text.config(state="normal")
        current_text = self.heard_text.get("1.0", "end-1c").strip()
        if not current_text:
            self.heard_text.insert(tk.END, "Recognized Text:\n", "black_text")
        self.heard_text.config(state="disabled")

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
            self.heard_text.config(state="normal")
            self.heard_text.delete("1.0", tk.END)
            self.heard_text.insert(tk.END, "Recognized Text:\n", "black_text")
            self.heard_text.config(state="disabled")
            self.after(100, self.listen_once)

    def listen_once(self):
        if not self._listening or not sr:
            return
        r = sr.Recognizer()
        with sr.Microphone() as mic:
            try:
                r.adjust_for_ambient_noise(mic, duration=0.5)
                audio = r.listen(mic, timeout=5, phrase_time_limit=8)
                text = r.recognize_google(audio)
            except Exception as e:
                messagebox.showerror("Speech Error", str(e))
                self._listening = False
                self.toggle_btn.config(text="🎤 Start")
                return

        self.heard_text.config(state="normal")
        self.heard_text.delete("1.0", tk.END)
        self.heard_text.insert(tk.END, "Recognized Text:\n", "black_text")
        self.heard_text.insert(tk.END, text, "blue_text")
        self.heard_text.config(state="disabled")

        self.add_msg("You", text, "user")

        mode = self.app.state.get("mode")
        if mode == "llm_interface":
            reply = generate_bot_reply(mode, text, app_state=self.app.state)
        else:
            reply = generate_bot_reply(mode, text)
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

    def _speak_run(self):
        try:
            # Always create a fresh engine
            self.engine = pyttsx3.init()
            self.engine.say(self._last_reply)
            self.engine.runAndWait()
        except Exception as e:
            print("TTS error:", e)
        self.after(0, self._stop_speaking_cleanup)

    def _stop_speaking_cleanup(self):
        self.speaking = False
        self.speak_btn.config(text="🔊 Speak")
        self.speak_btn.state(["!disabled"])  # Ensure button remains enabled
        self.engine = None  # Clear reference

    def on_clear(self):
    # (optional) stop any ongoing speech and reset the Speak button
       
        if self.speaking and self.engine:
            self.engine.stop()
       
        self._stop_speaking_cleanup()  # resets flags/button text safely

        # clear the chat history
        self.chat.config(state="normal")
        self.chat.delete("1.0", tk.END)
        self.chat.config(state="disabled")

        # forget the last reply so Speak is disabled until a new reply arrives
        self._last_reply = None
        self.speak_btn.state(["disabled"])