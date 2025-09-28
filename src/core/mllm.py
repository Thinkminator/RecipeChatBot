from typing import Optional
from PIL import Image

SINGAPORE_DISHES = [
    "Hainanese chicken rice",
    "Laksa",
    "Char kway teow",
    "Chilli crab",
    "Satay",
    "Roti prata",
    "Bak kut teh",
    "Nasi lemak",
    "Kaya toast",
    "Fish head curry",
    "Mee siam",
    "Chicken rice",
    "Wanton mee",
    "Hokkien mee",
    "Popiah",
    "Ice kacang",
    "Chendol",
    "Tau huay",
    "Carrot cake",
    "Otah"
]

def infer_dish_from_image(image_path: str, prompt: Optional[str] = None) -> Optional[str]:
    try:
        from transformers import CLIPProcessor, CLIPModel
        import torch

        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        image = Image.open(image_path).convert("RGB")

        if prompt:
            candidate_texts = [prompt] + SINGAPORE_DISHES
        else:
            candidate_texts = SINGAPORE_DISHES

        inputs = processor(text=candidate_texts, images=image, return_tensors="pt", padding=True)
        outputs = model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)

        best_idx = probs.argmax()
        confidence = probs[0, best_idx].item()

        if confidence > 0.3:
            return candidate_texts[best_idx]
    except Exception as e:
        print(f"CLIP error: {e}")

    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration

        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

        image = Image.open(image_path).convert("RGB")

        inputs = processor(image, return_tensors="pt")
        outputs = model.generate(**inputs)
        caption = processor.decode(outputs[0], skip_special_tokens=True)

        if prompt:
            combined_caption = f"{prompt}. {caption}"
        else:
            combined_caption = caption

        if len(combined_caption.split()) > 10:
            combined_caption = " ".join(combined_caption.split()[:6]).rstrip(",")

        return combined_caption
    except Exception as e:
        print(f"[vlm.infer_dish_from_image] Error running BLIP: {e}")
        return None


class MLLMInterface:

    def __init__(self, model, max_turns=100, global_prompt="", negative_prompt="", **generate_kwargs):
        self.model = model
        self.max_turns = max_turns
        self.global_prompt = global_prompt
        self.negative_prompt = negative_prompt
        self.generate_kwargs = generate_kwargs

    def generate(self, user_input: str, image_path: Optional[str] = None, streaming: bool = False):
        # If image_path is provided, infer dish name or caption
        if image_path:
            dish_name_or_caption = infer_dish_from_image(image_path, prompt=user_input)
            if dish_name_or_caption:
                combined_prompt = f"{dish_name_or_caption}. {user_input}"
            else:
                combined_prompt = user_input
        else:
            combined_prompt = user_input

        prompt = f"{self.global_prompt}\nUser: {combined_prompt}\nBot:"
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

                image_path = input("Image path (or press Enter to skip): ").strip()
                if image_path == "":
                    image_path = None

                response = self.generate(user_input, image_path=image_path)
                print("Bot:", response)