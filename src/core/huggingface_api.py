import os
from huggingface_hub import InferenceClient

# Initialize client.
# Optionally add provider="together" or base_url="https://<endpoint-url>/v1/" if using a specific provider/endpoint.
client = InferenceClient()

def query_huggingface(prompt: str, model: str = "deepseek-ai/DeepSeek-V3-0324") -> str:
    """
    model: optional Hugging Face model id (e.g. 'openai/gpt-oss-120b' or a provider-backed model).
           If None, the client will pick a recommended model for the task.
    """
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant. If the user is requesting a recipe, respond with the full recipe in a single paragraph without line breaks. For other questions, provide a concise answer."},
            {"role": "user", "content": prompt},
        ]

        response = client.chat.completions.create(
            messages=messages,
            model=model,         # pass None or a specific HF model id
            max_tokens=500,
            temperature=0.7,
        )

        # Response structure follows OpenAI-compatible format
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error communicating with Hugging Face Inference: {e}"