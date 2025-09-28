import tkinter as tk
from tkinter import ttk, messagebox
from .base_page import BasePage

GPT4ALL_MODELS = [
    "Meta-Llama-3-8B-Instruct.Q4_0.gguf",
    "Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf",
    "Phi-3-mini-4k-instruct.Q4_0.gguf",
    "orca-mini-3b-gguf2-q4_0.gguf",
    "gpt4all-13b-snoozy-q4_0.gguf"
]

class LLMParametersPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.title_var.set("LLM Parameters")
        self.selected_mode = None

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        for col in range(4):
            frame.grid_columnconfigure(col, weight=1)

        ttk.Label(frame, text="Select Model:").grid(row=0, column=0, sticky="w")
        self.model_var = tk.StringVar(value=GPT4ALL_MODELS[0])
        self.model_combo = ttk.Combobox(frame, textvariable=self.model_var, values=GPT4ALL_MODELS, state="readonly", width=40)
        self.model_combo.grid(row=0, column=1, columnspan=3, sticky="w")

        ttk.Label(frame, text="Max Turns:").grid(row=1, column=0, sticky="w", pady=(10,0))
        self.max_turns_var = tk.IntVar(value=100)
        ttk.Spinbox(frame, from_=1, to=1000, textvariable=self.max_turns_var, width=10).grid(row=1, column=1, sticky="w", pady=(10,0))

        ttk.Label(frame, text="Temperature:").grid(row=1, column=2, sticky="w", padx=(20,0), pady=(10,0))
        self.temperature_var = tk.DoubleVar(value=0.7)
        ttk.Spinbox(frame, from_=0.0, to=1.0, increment=0.01, textvariable=self.temperature_var, width=10).grid(row=1, column=3, sticky="w", pady=(10,0))

        ttk.Label(frame, text="Top-k:").grid(row=2, column=0, sticky="w", pady=(10,0))
        self.top_k_var = tk.IntVar(value=40)
        ttk.Spinbox(frame, from_=0, to=1000, textvariable=self.top_k_var, width=10).grid(row=2, column=1, sticky="w", pady=(10,0))

        ttk.Label(frame, text="Top-p:").grid(row=2, column=2, sticky="w", padx=(20,0), pady=(10,0))
        self.top_p_var = tk.DoubleVar(value=0.9)
        ttk.Spinbox(frame, from_=0.0, to=1.0, increment=0.01, textvariable=self.top_p_var, width=10).grid(row=2, column=3, sticky="w", pady=(10,0))

        ttk.Label(frame, text="Max Tokens:").grid(row=3, column=0, sticky="w", pady=(10,0))
        self.max_tokens_var = tk.IntVar(value=256)
        ttk.Spinbox(frame, from_=1, to=2048, textvariable=self.max_tokens_var, width=10).grid(row=3, column=1, sticky="w", pady=(10,0))

        ttk.Label(frame, text="Repetition Penalty:").grid(row=3, column=2, sticky="w", padx=(20,0), pady=(10,0))
        self.repetition_penalty_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(frame, from_=0.0, to=2.0, increment=0.01, textvariable=self.repetition_penalty_var, width=10).grid(row=3, column=3, sticky="w", pady=(10,0))

        ttk.Label(frame, text="Global Prompt:").grid(row=4, column=0, sticky="nw", pady=(10,0))
        self.global_prompt_text = tk.Text(frame, height=4, width=70)
        self.global_prompt_text.grid(row=4, column=1, columnspan=3, sticky="ew", pady=(10,0))

        ttk.Label(frame, text="Negative Prompt:").grid(row=5, column=0, sticky="nw", pady=(10,0))
        self.negative_prompt_text = tk.Text(frame, height=4, width=70)
        self.negative_prompt_text.grid(row=5, column=1, columnspan=3, sticky="ew", pady=(10,0))

        save_btn = ttk.Button(frame, text="Save", command=self.save_parameters)
        save_btn.grid(row=6, column=0, columnspan=4, pady=20, sticky="ew")

    def on_show(self, mode=None, **kwargs):
        self.selected_mode = mode or self.app.state.get("mode")
        params = self.app.state.get("llm_params", {})

        self.model_var.set(params.get("model", GPT4ALL_MODELS[0]))
        self.max_turns_var.set(params.get("max_turns", 100))
        self.temperature_var.set(params.get("temp", 0.7))  # renamed from temperature
        self.top_k_var.set(params.get("top_k", 40))
        self.top_p_var.set(params.get("top_p", 0.9))
        self.max_tokens_var.set(params.get("max_tokens", 256))
        self.repetition_penalty_var.set(params.get("repeat_penalty", 1.18))  # renamed from repetition_penalty
        self.global_prompt_text.delete("1.0", tk.END)
        self.global_prompt_text.insert(tk.END, params.get("global_prompt", ""))
        self.negative_prompt_text.delete("1.0", tk.END)
        self.negative_prompt_text.insert(tk.END, params.get("negative_prompt", ""))

    def save_parameters(self):
        params = {
            "model": self.model_var.get(),
            "max_turns": self.max_turns_var.get(),
            "temp": self.temperature_var.get(),  # renamed from temperature
            "top_k": self.top_k_var.get(),
            "top_p": self.top_p_var.get(),
            "max_tokens": self.max_tokens_var.get(),
            "repeat_penalty": self.repetition_penalty_var.get(),  # renamed from repetition_penalty
            "global_prompt": self.global_prompt_text.get("1.0", tk.END).strip(),
            "negative_prompt": self.negative_prompt_text.get("1.0", tk.END).strip(),
        }
        self.app.state["llm_params"] = params
        messagebox.showinfo("Saved", "LLM parameters saved.")
        if self.selected_mode == "mllm_interface":
            self.app.show("MLLMPage", mode=self.selected_mode)
        else:
            self.app.show("InputTypePage", mode=self.selected_mode)