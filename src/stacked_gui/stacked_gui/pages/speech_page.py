
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from .base_page import BasePage
from backend import generate_bot_reply
from tts import TTSController

try:
    import speech_recognition as sr
except Exception:
    sr = None

class SpeechPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.title_var.set("Speech Interface")

        # TTS
        self.tts = TTSController()

        # Use a content frame + grid so the input area is always visible
        content = ttk.Frame(self)
        content.pack(fill="both", expand=True)
        content.grid_rowconfigure(0, weight=1)     # chat expands
        content.grid_columnconfigure(0, weight=1)  # stretch horizontally

        # --- Chat history (top) ---------------------------------------------
        self.chat = scrolledtext.ScrolledText(content, wrap=tk.WORD, font=("Segoe UI", 12))
        self.chat.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 6))
        self.chat.tag_config("user", foreground="blue")
        self.chat.tag_config("bot", foreground="green", spacing3=8)
        self.chat.config(state="disabled")

        # --- Recognized text label ------------------------------------------
        self.heard_var = tk.StringVar(value="")
        ttk.Label(content, textvariable=self.heard_var, font=("Segoe UI", 11), foreground="blue")\
            .grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 6))

        self.status_var = tk.StringVar(value="")
        ttk.Label(content, textvariable=self.status_var, font=("Segoe UI", 9))\
            .grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 6))

        # --- Bottom row: input box (left) + control buttons (right) ---------
        self.input = tk.Text(content, height=3, font=("Segoe UI", 12), highlightthickness=1, highlightbackground="#bbb")
        self.input.grid(row=3, column=0, sticky="nsew", padx=(10, 6), pady=(0, 10))

        right = ttk.Frame(content)
        right.grid(row=3, column=1, sticky="ns", padx=(0, 10), pady=(0, 10))

        # Send manual text
        self.send_btn = ttk.Button(right, text="Send", width=14, command=self.on_submit)
        self.send_btn.pack(fill="x", pady=(0, 6))

        # Listening toggle
        self.toggle_btn = ttk.Button(right, text="🎤 Start", width=14, command=self.on_toggle_listen)
        self.toggle_btn.pack(fill="x", pady=(0, 6))

        # TTS buttons
        self.speak_btn = ttk.Button(right, text="Speak", width=14, command=self.on_speak)
        self.speak_btn.pack(fill="x", pady=(0, 6))
        self.stop_btn = ttk.Button(right, text="Stop Speech", width=14, command=self.on_stop_speech)
        self.stop_btn.pack(fill="x", pady=(0, 6))
        self.clear_btn = ttk.Button(right, text="Clear", width=14, command=self.on_clear)
        self.clear_btn.pack(fill="x")

        # Init button states
        self._listening = False
        self._last_reply = None
        self._update_tts_buttons(speaking=False)
        if not self.tts.available:
            self.speak_btn.state(["disabled"])
            self.stop_btn.state(["disabled"])

    def on_show(self, **_):
        mode = self.app.state.get("mode") or "—"
        self.title_var.set(f"Speech Interface — {mode.replace('_', ' ').title()}")
        self.set_back_enabled(True)

    def on_hide(self):
        if self._listening:
            self._listening = False
            self.toggle_btn.config(text="🎤 Start")
            self.status_var.set("Stopped listening.")
        try:
            self.tts.stop()
        except Exception:
            pass

    def add_msg(self, who, text, tag):
        self.chat.config(state="normal")
        self.chat.insert(tk.END, f"{who}: {text}\n", tag)
        self.chat.config(state="disabled")
        self.chat.yview(tk.END)

    def on_submit(self):
        # Send what's in the input box
        text = self.input.get("1.0", tk.END).strip()
        if not text:
            return
        self.input.delete("1.0", tk.END)
        self.add_msg("You", text, "user")
        reply = generate_bot_reply(self.app.state.get("mode"), text)
        self.add_msg("Bot", reply, "bot")
        self._last_reply = reply
        if self.tts.available:
            self.speak_btn.state(["!disabled"])

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

        # Put recognized text into the input area (so user can edit or hit Send)
        self.heard_var.set(text)
        self.input.delete("1.0", tk.END)
        self.input.insert("1.0", text)

        # Keep listening if toggle still on
        if self._listening:
            self.after(400, self.listen_once)

    def _tts_done(self):
        self.after(0, lambda: self._update_tts_buttons(speaking=False))

    def on_speak(self):
        if not self._last_reply:
            return
        if not self.tts.available:
            messagebox.showwarning("TTS not available", "pyttsx3 not installed.")
            return
        started = self.tts.start(self._last_reply, on_done=self._tts_done)
        if started:
            self._update_tts_buttons(speaking=True)

    def on_stop_speech(self):
        try:
            self.tts.stop()
        finally:
            self._update_tts_buttons(speaking=False)


    def on_clear(self):
        # Stop TTS and listening; clear UI fields
        try:
            self.tts.stop()
        except Exception:
            pass
        if self._listening:
            self._listening = False
            self.toggle_btn.config(text="🎤 Start")
            self.status_var.set("Stopped listening.")
        # Clear chat
        self.chat.config(state="normal")
        self.chat.delete("1.0", tk.END)
        self.chat.config(state="disabled")
        # Clear input and labels
        self.input.delete("1.0", tk.END)
        self.heard_var.set("")
        self.status_var.set("")
        # Reset reply and TTS buttons
        self._last_reply = None
        self._update_tts_buttons(speaking=False)

    def _update_tts_buttons(self, speaking: bool):
        if not self.tts.available:
            self.speak_btn.state(["disabled"])
            self.stop_btn.state(["disabled"])
            return
        if speaking:
            self.speak_btn.state(["disabled"])
            self.stop_btn.state(["!disabled"])
        else:
            if self._last_reply:
                self.speak_btn.state(["!disabled"])
            else:
                self.speak_btn.state(["disabled"])
            self.stop_btn.state(["disabled"])
