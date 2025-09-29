import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from gpt4all import GPT4All

from src.core.llm_adapter import gpt4all_model_list, LLMInterface

if __name__ == "__main__":
    model = GPT4All(gpt4all_model_list[2])
    print(f"model: f{gpt4all_model_list[2]}")
    llm = LLMInterface(model, max_tokens=100)
    llm.chat()