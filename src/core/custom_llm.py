"""
Custom LLM module for the Recipe ChatBot.
This module implements the T5 recipe generation model from Hugging Face.
"""
import os
from typing import List

# Attempt to support both Flax/JAX and PyTorch backends.
try:
    # JAX/Flax path
    from transformers import FlaxAutoModelForSeq2SeqLM, AutoTokenizer
    import jax
    JAX_AVAILABLE = True
    torch = None
except Exception:
    try:
        # PyTorch path
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        import torch
        JAX_AVAILABLE = False
    except Exception:
        JAX_AVAILABLE = False
        torch = None

class RecipeGenerator:
    def __init__(self, model_name: str = "flax-community/t5-recipe-generation"):
        """
        Initialize the RecipeGenerator with the T5 recipe generation model.

        Args:
            model_name (str): The Hugging Face model identifier
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.special_tokens = None
        self.tokens_map = {
            "<sep>": "--",
            "<section>": "\n"
        }

        # Generation parameters (from model card examples)
        self.generation_kwargs = {
            "max_length": 512,
            "min_length": 64,
            "no_repeat_ngram_size": 3,
            "do_sample": True,
            "top_k": 60,
            "top_p": 0.95
        }

        self._load_model()

    def _load_model(self):
        """Load the Hugging Face model and tokenizer."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)
            self.special_tokens = self.tokenizer.all_special_tokens

            if JAX_AVAILABLE:
                self.model = FlaxAutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            else:
                # PyTorch
                self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        except Exception as e:
            raise Exception(f"Failed to load model {self.model_name}: {e}")

    def _skip_special_tokens(self, text: str) -> str:
        """Remove special tokens from the generated text."""
        if self.special_tokens:
            for token in self.special_tokens:
                text = text.replace(token, "")
        return text

    def _postprocess_text(self, texts: List[str]) -> List[str]:
        """
        Post-process the generated text to make it more readable.
        """
        if not isinstance(texts, list):
            texts = [texts]

        new_texts = []
        for text in texts:
            # Remove special tokens
            text = self._skip_special_tokens(text)

            # Replace tokens according to mapping
            for k, v in self.tokens_map.items():
                text = text.replace(k, v)

            new_texts.append(text)
        return new_texts

    def _format_recipe(self, recipe_text: str) -> str:
        """
        Format the raw recipe text into a structured format: TITLE, INGREDIENTS, DIRECTIONS.
        """
        sections = recipe_text.split("\n")
        formatted_sections = []

        for section in sections:
            section = section.strip()
            if not section:
                continue

            if section.lower().startswith("title:"):
                section = section[len("title:"):].strip().capitalize()
                formatted_sections.append(f"[TITLE]: {section}")
            elif section.lower().startswith("ingredients:"):
                section = section[len("ingredients:"):].strip()
                ingredients = [
                    f"  - {i+1}: {info.strip().capitalize()}"
                    for i, info in enumerate(section.split("--")) if info.strip()
                ]
                if ingredients:
                    formatted_sections.append("[INGREDIENTS]:")
                    formatted_sections.extend(ingredients)
            elif section.lower().startswith("directions:"):
                section = section[len("directions:"):].strip()
                directions = [
                    f"  - {i+1}: {info.strip().capitalize()}"
                    for i, info in enumerate(section.split("--")) if info.strip()
                ]
                if directions:
                    formatted_sections.append("[DIRECTIONS]:")
                    formatted_sections.extend(directions)

        return "\n".join(formatted_sections)

    def generate_recipe(self, ingredients: str) -> str:
        """
        Generate a recipe from a comma-separated list of ingredients.

        Args:
            ingredients (str): Comma-separated list of ingredients

        Returns:
            str: Generated recipe in formatted text
        """
        if not self.model or not self.tokenizer:
            raise Exception("Model not loaded properly")

        try:
            prefix = "items: "
            input_text = prefix + ingredients

            # Tokenize input - choose tensor backend per availability
            if JAX_AVAILABLE:
                inputs = self.tokenizer(
                    input_text,
                    max_length=256,
                    padding="max_length",
                    truncation=True,
                    return_tensors="jax"
                )

                input_ids = inputs.input_ids
                attention_mask = inputs.attention_mask

                output_ids = self.model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    **self.generation_kwargs
                )
                generated = output_ids.sequences
                generated_recipe = self.tokenizer.batch_decode(generated, skip_special_tokens=False)
            else:
                # PyTorch path
                inputs = self.tokenizer(
                    input_text,
                    max_length=256,
                    padding="max_length",
                    truncation=True,
                    return_tensors="pt"
                )
                input_ids = inputs.input_ids
                attention_mask = inputs.attention_mask

                with torch.no_grad():
                    output_ids = self.model.generate(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        **self.generation_kwargs
                    )
                generated_recipe = self.tokenizer.batch_decode(output_ids, skip_special_tokens=False)

            # Post-process and format
            processed_recipe = self._postprocess_text(generated_recipe)
            if processed_recipe:
                formatted_recipe = self._format_recipe(processed_recipe[0])
                return formatted_recipe or "Sorry, I couldn't generate a recipe with the provided ingredients."
            else:
                return "Sorry, I couldn't generate a recipe with the provided ingredients."

        except Exception as e:
            return f"Error generating recipe: {e}"


# Singleton helper
_recipe_generator = None

def get_recipe_generator() -> RecipeGenerator:
    global _recipe_generator
    if _recipe_generator is None:
        _recipe_generator = RecipeGenerator()
    return _recipe_generator

def generate_recipe_from_ingredients(ingredients: str) -> str:
    generator = get_recipe_generator()
    return generator.generate_recipe(ingredients)

# Quick test (run module directly)
if __name__ == "__main__":
    ingredients = "macaroni, butter, salt, bacon, milk, flour, pepper, cream corn"
    print("Generating recipe for:", ingredients)
    print(generate_recipe_from_ingredients(ingredients))