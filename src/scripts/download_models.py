import os
import requests

models = [
    "Meta-Llama-3-8B-Instruct.Q4_0.gguf",
    "Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf",
    "Phi-3-mini-4k-instruct.Q4_0.gguf",
    "orca-mini-3b-gguf2-q4_0.gguf",
    "gpt4all-13b-snoozy-q4_0.gguf"
]

base_url = "https://gpt4all.io/models/"

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
target_dir = os.path.join(project_root, "data", "models", "gpt4all")
os.makedirs(target_dir, exist_ok=True)

for model in models:
    url = base_url + model
    target_path = os.path.join(target_dir, model)
    if os.path.exists(target_path):
        print(f"{model} already exists, skipping.")
        continue
    print(f"Downloading {model}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(target_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded {model} successfully.")
    else:
        print(f"Failed to download {model}. HTTP status code: {response.status_code}")