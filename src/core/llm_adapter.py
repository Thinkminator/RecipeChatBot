# GPT4All model name
gpt4all_model_list = [
    "Meta-Llama-3-8B-Instruct.Q4_0.gguf",
    "Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf",
    "Phi-3-mini-4k-instruct.Q4_0.gguf",
    "orca-mini-3b-gguf2-q4_0.gguf",
    "gpt4all-13b-snoozy-q4_0.gguf"
]

# Multi-turn LLM
class LLMInterface:

    def __init__(self, model, max_turns=100, global_prompt="", negative_prompt="", **generate_kwargs):
        self.model = model
        self.max_turns = max_turns
        self.global_prompt = global_prompt
        self.negative_prompt = negative_prompt
        self.generate_kwargs = generate_kwargs

    def generate(self, user_input: str, streaming: bool = False):
        prompt = f"{self.global_prompt}\nUser: {user_input}\nBot:"
        if self.negative_prompt:
            prompt += f"\nAvoid: {self.negative_prompt}"

        return self.model.generate(prompt, streaming=streaming, **self.generate_kwargs)

    def chat(self):
        print("Starting multi-turn dialogue. Type 'exit' to quit.")
        with self.model.chat_session():
            for i in range(self.max_turns):
                user_input = input("You: ")
                if user_input.strip().lower() in ["exit", "quit"]:
                    print("Exiting chat.")
                    break
                response = self.generate(user_input)
                print("Bot:", response)
                