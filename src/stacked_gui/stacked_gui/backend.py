
"""
backend.py (strict, with helpful path handling)

Fixes "No module named 'src'" by searching upward for a 'src' folder and
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
    from src.core.huggingface_api import query_huggingface
    from src.core.custom_llm import generate_recipe_from_ingredients
except ModuleNotFoundError as e:
    # As a convenience, also try without the 'src.' prefix in case your package
    # is installed directly as 'core'.
    try:
        from core.nlu import find_dish_in_text
        from core.knowledge import get_recipe
        from core.huggingface_api import query_huggingface
        from core.custom_llm import generate_recipe_from_ingredients
    except ModuleNotFoundError:
        raise ImportError(
            "Could not import your backend modules. Make sure either:\n"
            "  1) You run the app from the project root and it contains a 'src/' folder, OR\n"
            "  2) You set PYTHONPATH to the project root (e.g., PYTHONPATH=. python stacked_gui/app.py), OR\n"
            "  3) You installed your package (e.g., `pip install -e .`) so imports like 'src.core.*' work.\n"
            "If your package name is different, update the import lines in backend.py accordingly."
        ) from e


def generate_bot_reply(mode: str, user_text: str) -> str:
    """Route to your real backends based on selected mode."""
    mode = (mode or "").strip() or "existing_recipe"
    if mode == "existing_recipe":
        dish = find_dish_in_text(user_text)
        if dish:
            return get_recipe(dish)
        return "Sorry, I couldn't find a matching recipe."
    elif mode == "huggingface":
        return query_huggingface(user_text)
    elif mode == "custom_model":
        return generate_recipe_from_ingredients(user_text)
    else:
        # Task 2 or other experimental modes — delegate/adjust as you wish
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
