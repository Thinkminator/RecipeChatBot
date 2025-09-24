
from tkinter import ttk
from .base_page import BasePage

class InputTypePage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)

        self.mode_label = ttk.Label(self, text="", font=("Segoe UI", 11))
        self.mode_label.pack(pady=(0, 8))

        btns = ttk.Frame(self)
        btns.pack(pady=20)

        ttk.Button(btns, text="Text Interface", width=20,
                   command=lambda: self.app.show("TextPage")).pack(pady=8)

        ttk.Button(btns, text="Speech Interface", width=20,
                   command=lambda: self.app.show("SpeechPage")).pack(pady=8)

    def on_show(self, mode=None, **_):
        mode = mode or self.app.state.get("mode")
        self.app.state["mode"] = mode
        nice = (mode or "").replace("_", " ").title() or "—"
        self.title_var.set("Input Type")
        self.mode_label.config(text=f"Mode: {nice}")
        self.set_back_enabled(True)
