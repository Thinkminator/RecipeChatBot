"""
backend.py (strict, with helpful path handling)

Fixes "No module named 'src'" by searching upward for a 'src' directory and
adding its parent to sys.path at runtime. Then imports your real modules.
"""

import sys, os
from pathlib import Path

# --- Locate a nearby 'src' directory and add its parent to sys.path ---------
_THIS = Path(__file__).resolve()
candidates = [_THIS.parent, _THIS.parent.parent, _THIS.parent.parent.parent]
for base in candidates:
    src_dir = base / "src"
    if src_dir.exists() and src_dir.is_dir():
        sys.path.insert(0, str(base))  # so 'import src.*' works
        break

# --- Now import your real backends (adjust module paths if needed) -----------
try:
    from src.core.nlu import find_dish_in_text
    from src.core.knowledge import get_recipe
    from src.core.themealdb_api import query_themealdb
    from src.core.custom_llm import generate_recipe_from_ingredients
    from src.core.vlm import infer_dish_from_image
    from src.core.llm_adapter import gpt4all_model_list, LLMInterface
    from gpt4all import GPT4All
except ModuleNotFoundError as e:
    # As a convenience, also try without the 'src.' prefix in case your package
    # is installed directly as 'core'.
    try:
        from core.nlu import find_dish_in_text
        from core.knowledge import get_recipe
        from core.themealdb_api import query_themealdb
        from core.custom_llm import generate_recipe_from_ingredients
        from core.vlm import infer_dish_from_image
        from gpt4all import GPT4All
        from src.core.llm_adapter import gpt4all_model_list, LLMInterface
    except ModuleNotFoundError:
        raise ImportError(
            "Could not import your backend modules. Make sure either:\n"
            "  1) You run the app from the project root and it contains a 'src/' folder, OR\n"
            "  2) You set PYTHONPATH to the project root (e.g., PYTHONPATH=. python stacked_gui/app.py), OR\n"
            "  3) You installed your package (e.g., `pip install -e .`) so imports like 'src.core.*' work.\n"
            "If your package name is different, update the import lines in backend.py accordingly."
        ) from e

_gpt4all_instance = None

def _get_gpt4all_instance(app_state=None):
    global _gpt4all_instance
    if GPT4All is None or LLMInterface is None:
        raise RuntimeError("GPT4All or LLMInterface not available")

    params = app_state.get("llm_params", {}) if app_state else {}
    model_name = params.get("model")
    if not model_name:
        raise RuntimeError("No GPT4All model selected")
    print(f"DEBUG: Using GPT4All model: {model_name}")

    try:
        model = GPT4All(model_name)  # This will download if not found
    except Exception as e:
        raise RuntimeError(f"Failed to load or download GPT4All model '{model_name}': {e}")

    generate_kwargs = {
        "temp": params.get("temp", 0.7),
        "top_k": params.get("top_k", 40),
        "top_p": params.get("top_p", 0.9),
        "max_tokens": params.get("max_tokens", 200),
        "repeat_penalty": params.get("repeat_penalty", 1.18),
    }

    _gpt4all_instance = LLMInterface(
        model,
        max_turns=params.get("max_turns", 100),
        global_prompt=params.get("global_prompt", "You are a helpful cooking assistant, return only recipe in 1 paragraph."),
        negative_prompt=params.get("negative_prompt", "Avoid: Too long"),
        **generate_kwargs
    )
    return _gpt4all_instance

def generate_bot_reply(mode: str, user_text: str, *, app_state: dict = None) -> str:
    """Route to your real backends based on selected mode."""
    mode = (mode or "").strip() or "existing_recipe"
    if mode == "existing_recipe":
        dish = find_dish_in_text(user_text)
        if dish:
            return get_recipe(dish)
        return "Sorry, I couldn't find a matching recipe."
    elif mode == "themealdb":
        return query_themealdb(user_text)
    elif mode == "custom_model":
        return generate_recipe_from_ingredients(user_text)
    elif mode == "llm_interface":
        try:
            llm = _get_gpt4all_instance(app_state=app_state)
            return llm.generate(user_text)
        except Exception as e:
            return f"Error with GPT4All model: {e}"
    else:
        return f"[{mode}] {user_text}"


def speak_text(text: str) -> bool:
    """Speak text via pyttsx3 if available. Returns True if spoken, False otherwise."""
    try:
        import pyttsx3
    except Exception:
        return False
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception:
        return False