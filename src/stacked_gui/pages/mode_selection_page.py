from tkinter import ttk
from .base_page import BasePage

class ModeSelectionPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.title_var.set("Mode Selection")

        # Create a style for bigger buttons
        style = ttk.Style()
        style.configure("Big.TButton", font=("Segoe UI", 14), padding=10)

        body = ttk.Frame(self)
        body.pack(expand=True)

        ttk.Label(body, text="Choose model mode:", font=("Segoe UI", 16)).pack(pady=12)

        btns = ttk.Frame(body)
        btns.pack(pady=10)

        def go(mode):
            self.app.state["mode"] = mode
            if mode == "llm_interface" or mode == "mllm_interface":
                self.app.show("LLMParametersPage", mode=mode)
            else:
                self.app.show("InputTypePage", mode=mode)

        modes = [
            ("Existing Recipe", "existing_recipe"),
            ("TheMealDB", "themealdb"),
            ("Custom Model", "custom_model"),
            ("LLM Interface", "llm_interface"),
            ("MLLM Interface", "mllm_interface"),
        ]
        for label, mode in modes:
            ttk.Button(btns, text=label, width=24, style="Big.TButton", command=lambda m=mode: go(m)).pack(pady=8)

    def on_show(self, **kwargs):
        # Disable Back on root page
        self.set_back_enabled(False)