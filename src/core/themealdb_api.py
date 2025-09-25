import requests

def extract_dish_name(prompt: str) -> str:
    """
    Extract dish name from natural language prompts like:
    - "how to cook Chicken Chop"
    - "recipe for Arrabiata"
    - "make Beef Stew"
    """
    prompt = prompt.strip().lower()
    for prefix in [
        "how to cook ",
        "how do you cook ",
        "recipe for ",
        "make ",
        "prepare ",
        "cook ",
        "how to make "
    ]:
        if prompt.startswith(prefix):
            return prompt[len(prefix):].strip().rstrip("?.,!")
    return prompt  # fallback: return as-is

def query_themealdb(prompt: str, model: str = None) -> str:
    """
    Replacement for Hugging Face LLM query using TheMealDB API.
    The 'model' parameter is ignored for compatibility.
    """
    try:
        # Extract dish name from natural language prompt
        dish_name = extract_dish_name(prompt)

        # TheMealDB search endpoint (no API key needed)
        url = "https://www.themealdb.com/api/json/v1/1/search.php"
        params = {"s": dish_name}

        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return f"Error: Received status code {response.status_code}"

        data = response.json()

        meals = data.get("meals")
        if not meals:
            return "Sorry, I couldn't find any recipes for that."

        meal = meals[0]

        name = meal.get("strMeal", "Unknown")
        instructions = meal.get("strInstructions", "").replace("\n", " ").strip()
        ingredients = []

        for i in range(1, 21):
            ingredient = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            if ingredient and ingredient.strip():
                ingredients.append(f"{measure} {ingredient}".strip())

        recipe_text = (
            f"Recipe for {name}:\n\n"
            f"Ingredients:\n" + "\n".join(f"- {ing}" for ing in ingredients) + "\n\n"
            f"Instructions:\n{instructions}"
        )

        return recipe_text

    except Exception as e:
        return f"Error communicating with TheMealDB: {e}"