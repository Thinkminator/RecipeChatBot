
import tkinter as tk
from tkinter import ttk

class BasePage(ttk.Frame):
    """Base page with a standard self.header and Back button."""
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.header = ttk.Frame(self)
        self.header .pack(fill="x", padx=10, pady=(10, 0))

        self.back_btn = ttk.Button(self.header , text="⟵ Back", command=self.app.back)
        self.back_btn.pack(side="left")

        self.title_var = tk.StringVar(value="")
        ttk.Label(self.header , textvariable=self.title_var, font=("Segoe UI", 16)).pack(side="left", padx=10)

        ttk.Separator(self).pack(fill="x", padx=10, pady=10)

    # Optional lifecycle hooks
    def on_show(self, **kwargs):  # called by router when page is shown
        pass

    def on_hide(self):  # called by router when page is hidden
        pass

    def set_back_enabled(self, ok: bool):
        if ok:
            self.back_btn.state(["!disabled"])
        else:
            self.back_btn.state(["disabled"])
