"""
Custom LLM module for the Recipe ChatBot.
This module implements the T5 recipe generation model from Hugging Face.
"""
import os
from typing import List
import re
import ast

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

        # Generation parameters adjusted per backend
        if JAX_AVAILABLE:
            # JAX/Flax generate() supports fewer args
            self.generation_kwargs = {
                "max_length": 512,
                "min_length": 64,
                "no_repeat_ngram_size": 3,
                "do_sample": False,  # deterministic output
            }
        else:
            # PyTorch supports full set
            self.generation_kwargs = {
                "max_length": 512,
                "min_length": 64,
                "no_repeat_ngram_size": 3,
                "do_sample": False,  # deterministic output
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
        Format the raw recipe text into a structured format: TITLE and DIRECTIONS only (exclude INGREDIENTS).
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
            # Skip ingredients section entirely
            elif section.lower().startswith("ingredients:"):
                continue
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

    def _extract_ingredients(self, prompt_text: str) -> str:
        """
        Extract the ingredients list from the prompt text and convert to comma-separated string.

        Args:
            prompt_text (str): Full prompt text containing 'ingredients: [...]'

        Returns:
            str: Comma-separated ingredients string
        """
        match = re.search(r'ingredients:\s*(\[[^\]]*\])', prompt_text, re.IGNORECASE)
        if match:
            try:
                ingredients_list = ast.literal_eval(match.group(1))
                if isinstance(ingredients_list, list):
                    return ", ".join(ingredients_list)
            except Exception:
                pass
        return ""

    def generate_recipe(self, prompt_text: str) -> str:
        """
        Generate a recipe from a full prompt text (e.g., title + ingredients).

        Args:
            prompt_text (str): Full prompt text including title and ingredients

        Returns:
            str: Generated recipe in formatted text
        """
        if not self.model or not self.tokenizer:
            raise Exception("Model not loaded properly")

        try:
            # Extract ingredients and prepare input in expected format
            ingredients_str = self._extract_ingredients(prompt_text)
            if not ingredients_str:
                return "Could not extract ingredients from the prompt."

            input_text = "items: " + ingredients_str.strip()

            # Tokenize input - choose tensor backend per availability
            if JAX_AVAILABLE:
                inputs = self.tokenizer(
                    input_text,
                    max_length=512,
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
                    max_length=512,
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
                return formatted_recipe or "Sorry, I couldn't generate a recipe with the provided prompt."
            else:
                return "Sorry, I couldn't generate a recipe with the provided prompt."

        except Exception as e:
            return f"Error generating recipe: {e}"


# Singleton helper
_recipe_generator = None

def get_recipe_generator() -> RecipeGenerator:
    global _recipe_generator
    if _recipe_generator is None:
        _recipe_generator = RecipeGenerator()
    return _recipe_generator

def generate_recipe_from_ingredients(prompt_text: str) -> str:
    generator = get_recipe_generator()
    return generator.generate_recipe(prompt_text)