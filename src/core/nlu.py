import string
import os

RECIPE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'recipes')

def normalize_text(text):
    """Lowercase and remove punctuation from text."""
    text = text.lower()
    return text.translate(str.maketrans('', '', string.punctuation))

def load_dish_keywords():
    """Load recipe filenames and create a dict mapping dish name to keywords list."""
    dish_keywords = {}
    for filename in os.listdir(RECIPE_DIR):
        if filename.endswith('.txt'):
            dish_name = filename[:-4]  # remove .txt
            keywords = dish_name.split('_')
            dish_keywords[dish_name] = keywords
    return dish_keywords

def find_dish_in_text(user_input):
    """
    Find the best matching dish name in user input.
    Returns dish_name or None.
    """
    normalized_input = normalize_text(user_input)
    input_words = set(normalized_input.split())

    dish_keywords = load_dish_keywords()

    best_match = None
    max_matches = 0

    for dish_name, keywords in dish_keywords.items():
        # Count how many keywords appear in input
        matches = sum(1 for kw in keywords if kw in input_words)
        if matches > max_matches:
            max_matches = matches
            best_match = dish_name

    # Return best match only if at least one keyword matched
    if max_matches > 0:
        return best_match
    else:
        return None

# Example usage
if __name__ == "__main__":
    test_sentences = [
        "Can you tell me how to cook Katong Laksa?",
        "I want the recipe for chili crab please.",
        "How to make chicken rice?",
        "Do you have bak kut teh recipe?",
        "I want some char kway teow."
    ]
    for sentence in test_sentences:
        dish = find_dish_in_text(sentence)
        print(f"Input: {sentence}\nMatched dish: {dish}\n")