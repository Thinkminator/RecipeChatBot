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

def infer_dish_from_image(image_path: str) -> Optional[str]:
    try:
        from transformers import CLIPProcessor, CLIPModel

        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        image = Image.open(image_path).convert("RGB")

        inputs = processor(text=SINGAPORE_DISHES, images=image, return_tensors="pt", padding=True)
        outputs = model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)

        best_idx = probs.argmax()
        confidence = probs[0, best_idx].item()

        if confidence > 0.3:
            return SINGAPORE_DISHES[best_idx]
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

        if len(caption.split()) > 10:
            caption = " ".join(caption.split()[:6]).rstrip(",")
        return caption
    except Exception as e:
        print(f"[vlm.infer_dish_from_image] Error running BLIP: {e}")
        return None