import os

RECIPE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'recipes')

def get_recipe(dish_name):
    """
    Given a dish name (without .txt), return the recipe text.
    If not found, return an error message.
    """
    if not dish_name:
        return "Sorry, I couldn't find the dish in your query."

    recipe_path = os.path.join(RECIPE_DIR, dish_name + ".txt")
    if os.path.exists(recipe_path):
        with open(recipe_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return f"Sorry, the recipe for '{dish_name.replace('_', ' ')}' is not available."

# Example usage
if __name__ == "__main__":
    test_dishes = ["chicken_rice", "katong_laksa", "non_existent_dish"]
    for dish in test_dishes:
        print(f"Recipe for {dish}:\n{get_recipe(dish)}\n{'-'*40}\n")