from tkinter import ttk
from .base_page import BasePage

class InputTypePage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)

        style = ttk.Style()
        style.configure("Big.TButton", font=("Segoe UI", 14), padding=10)

        self.mode_label = ttk.Label(self, text="", font=("Segoe UI", 14))
        self.mode_label.pack(pady=(0, 12))

        btns = ttk.Frame(self)
        btns.pack(pady=20)

        ttk.Button(btns, text="Text Interface", width=20,
                   style="Big.TButton",
                   command=lambda: self.app.show("TextPage")).pack(pady=12)

        ttk.Button(btns, text="Speech Interface", width=20,
                   style="Big.TButton",
                   command=lambda: self.app.show("SpeechPage")).pack(pady=12)
        
        ttk.Button(btns, text="Image Interface", width=20,
                   style="Big.TButton",
                   command=lambda: self.app.show("ImagePage")).pack(pady=12)

    def on_show(self, mode=None, **_):
        mode = mode or self.app.state.get("mode")
        self.app.state["mode"] = mode
        nice = (mode or "").replace("_", " ").title() or "—"
        self.title_var.set("Input Type")
        self.mode_label.config(text=f"Mode: {nice}")
        self.set_back_enabled(True)