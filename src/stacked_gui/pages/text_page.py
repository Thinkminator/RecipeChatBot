import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from .base_page import BasePage
from backend import generate_bot_reply
import pyttsx3
from threading import Thread

class TextPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.title_var.set("Text Interface")

        # Input area
        row = ttk.Frame(self)
        row.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
        row.pack_propagate(False)
        row.configure(height=60)

        side = ttk.Frame(row, width=110)
        side.pack(side="right", padx=(8, 0), fill="y")
        side.pack_propagate(False)

        self.input = tk.Text(row, height=2, font=("Segoe UI", 12), width=50)
        self.input.pack(side="left", fill="both", expand=True)

        ttk.Button(side, text="➤ Send", width=10, command=self.on_submit).pack(fill="x", pady=(0, 4))

        self.speak_btn = ttk.Button(side, text="🔊 Speak", width=10, command=self.on_speak, state="disabled")
        self.speak_btn.pack(fill="x")

        # Chat display
        self.chat = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Segoe UI", 12))
        self.chat.pack(fill="both", expand=True, padx=10, pady=(10, 6))
        self.chat.tag_config("user", foreground="blue")
        self.chat.tag_config("bot", foreground="green", spacing3=8)
        self.chat.config(state="disabled")

        # TTS state
        self._last_reply = None
        self.speaking = False
        self.engine = None

    def on_show(self, **_):
        mode = self.app.state.get("mode") or "—"
        self.title_var.set(f"Text Interface — {mode.replace('_', ' ').title()}")
        self.input.focus_set()

    def add_msg(self, who, text, tag):
        self.chat.config(state="normal")
        self.chat.insert(tk.END, f"{who}: {text}\n", tag)
        self.chat.config(state="disabled")
        self.chat.yview(tk.END)

    def on_submit(self):
        text = self.input.get("1.0", tk.END).strip()
        if not text:
            return
        self.input.delete("1.0", tk.END)
        self.add_msg("You", text, "user")

        mode = self.app.state.get("mode")
        if mode == "llm_interface":
            reply = generate_bot_reply(mode, text, app_state=self.app.state)
        else:
            reply = generate_bot_reply(mode, text)
        self.add_msg("Bot", reply, "bot")
        self._last_reply = reply
        self.speak_btn.state(["!disabled"])
        self.speak_btn.config(text="🔊 Speak")

    def on_speak(self):
        if not self._last_reply:
            return

        if not self.speaking:
            # Start speaking in background thread
            self.speaking = True
            self.speak_btn.config(text="✖ Cancel")
            Thread(target=self._speak_run, daemon=True).start()
        else:
            # Stop speaking
            try:
                if self.engine:
                    self.engine.stop()
            except Exception:
                pass
            self._stop_speaking_cleanup()

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