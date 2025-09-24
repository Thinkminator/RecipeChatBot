
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from .base_page import BasePage
from backend import generate_bot_reply
from tts import TTSController

class TextPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.title_var.set("Text Interface")

        # TTS controller
        self.tts = TTSController()

        # Use a dedicated content frame and GRID inside it.
        content = ttk.Frame(self)
        content.pack(fill="both", expand=True)

        # Layout: row 0 = chat (expands), row 1 = input + buttons (fixed height)
        content.grid_rowconfigure(0, weight=1)   # chat grows
        content.grid_columnconfigure(0, weight=1)  # input/chat stretch horizontally

        # --- Chat area -------------------------------------------------------
        self.chat = scrolledtext.ScrolledText(content, wrap=tk.WORD, font=("Segoe UI", 12))
        self.chat.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 6))
        self.chat.tag_config("user", foreground="blue")
        self.chat.tag_config("bot", foreground="green", spacing3=8)
        self.chat.config(state="disabled")

        # --- Bottom row: input (left) + buttons (right) ----------------------
        self.input = tk.Text(content, height=4, font=("Segoe UI", 12), highlightthickness=1, highlightbackground="#bbb")
        self.input.grid(row=1, column=0, sticky="nsew", padx=(10, 6), pady=(0, 10))

        side = ttk.Frame(content)
        side.grid(row=1, column=1, sticky="ns", padx=(0, 10), pady=(0, 10))

        self.send_btn = ttk.Button(side, text="Send", width=12, command=self.on_submit)
        self.send_btn.pack(fill="x")

        # Speak / Stop buttons
        self.speak_btn = ttk.Button(side, text="Speak", width=12, command=self.on_speak)
        self.speak_btn.pack(fill="x", pady=(8, 0))
        self.stop_btn = ttk.Button(side, text="Stop Speech", width=12, command=self.on_stop_speech)
        self.stop_btn.pack(fill="x", pady=(8, 0))

        # Clear chat/input
        self.clear_btn = ttk.Button(side, text="Clear", width=12, command=self.on_clear)
        self.clear_btn.pack(fill="x", pady=(8, 0))

        # Start with speak disabled until we have a reply; stop disabled unless speaking
        self._last_reply = None
        self._update_tts_buttons(speaking=False)

        if not self.tts.available:
            self.speak_btn.state(["disabled"])
            self.stop_btn.state(["disabled"])

    def on_show(self, **_):
        mode = self.app.state.get("mode") or "—"
        self.title_var.set(f"Text Interface — {mode.replace('_', ' ').title()}")
        self.set_back_enabled(True)
        self.input.focus_set()

    def on_hide(self):
        # Stop any ongoing TTS when leaving the page
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

    def _tts_done(self):
        # Called from worker thread; marshal back to UI thread
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
        # Stop any ongoing speech and clear UI
        try:
            self.tts.stop()
        except Exception:
            pass
        # Clear chat
        self.chat.config(state="normal")
        self.chat.delete("1.0", tk.END)
        self.chat.config(state="disabled")
        # Clear input
        self.input.delete("1.0", tk.END)
        # Reset last reply and buttons
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
            # enable Speak only if we have something to say
            if self._last_reply:
                self.speak_btn.state(["!disabled"])
            else:
                self.speak_btn.state(["disabled"])
            self.stop_btn.state(["disabled"])
