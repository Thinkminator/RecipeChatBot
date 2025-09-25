
"""
app.py
Router-based Tkinter app that stacks pages in a single Tk() and supports Back navigation.
Run:  python app.py
"""
import tkinter as tk
from tkinter import ttk
from pages import ModeSelectionPage, InputTypePage, TextPage, SpeechPage, ImagePage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Recipe Chatbot")
        self.geometry("600x560")
        self.minsize(600, 560)
        self.maxsize(600, 560) 

        # Shared global state (selected mode, etc.)
        self.state = {"mode": None}

        # Single container for all pages
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.pages = {}
        self.history = []
        self.current = None

        # Register pages
        for P in (ModeSelectionPage, InputTypePage, TextPage, SpeechPage, ImagePage):
            page = P(self.container, self)
            self.pages[P.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        # Start at main page
        self.show("ModeSelectionPage", remember=False)

    def show(self, name, *, remember=True, **kwargs):
        target = self.pages[name]
        if self.current and remember and self.current is not target:
            self.history.append(self.current)
            if hasattr(self.current, "on_hide"):
                self.current.on_hide()

        if hasattr(target, "on_show"):
            target.on_show(**kwargs)

        target.tkraise()
        self.current = target
        if hasattr(self.current, "set_back_enabled"):
            self.current.set_back_enabled(bool(self.history))

    def back(self):
        if not self.history:
            return
        prev = self.history.pop()
        if hasattr(self.current, "on_hide"):
            self.current.on_hide()
        prev.tkraise()
        self.current = prev
        if hasattr(self.current, "set_back_enabled"):
            self.current.set_back_enabled(bool(self.history))


if __name__ == "__main__":
    App().mainloop()
