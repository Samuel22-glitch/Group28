#parsing and cleaning the recipe's ingredient 

import html
import math
import re

# Unit name aliases
standardUnit = {
    "tbsp": "tbsp", "tbs": "tbsp", "tblsp": "tbsp",
    "tablespoon": "tbsp", "tablespoons": "tbsp",
    "tsp": "tsp", "teaspoon": "tsp", "teaspoons": "tsp",
    "cup": "cup", "cups": "cup",
    "g": "g", "gram": "g", "grams": "g",
    "kg": "kg", "kilogram": "kg", "kilograms": "kg",
    "ml": "ml", "millilitre": "ml", "millilitres": "ml",
    "milliliter": "ml", "milliliters": "ml",
    "l": "l", "litre": "l", "litres": "l", "liter": "l", "liters": "l",
    "oz": "oz", "ounce": "oz", "ounces": "oz",
    "lb": "lb", "lbs": "lb", "pound": "lb", "pounds": "lb",
    "clove": "clove", "cloves": "clove",
    "slice": "slice", "slices": "slice",
}


fractions = {
    "½": "1/2", "⅓": "1/3", "⅔": "2/3", "¼": "1/4", "¾": "3/4",
    "⅕": "1/5", "⅛": "1/8", "⅜": "3/8", "⅝": "5/8", "⅞": "7/8",
}

numbers = r"\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?"

measurement = re.compile(r"^\s*(" + numbers + r")\s*([a-zA-Z]*)\s*(.*)$")

patternRange = re.compile(r"^(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)")


def clean_text(text):
    if not text:
        return ""
    text = html.unescape(str(text))
    text = text.replace("\u00a0", " ")
    text = text.replace("–", "-").replace("—", "-")
    for symbol, fraction in fractions.items():
        text = text.replace(symbol, " " + fraction + " ")
    text = " ".join(text.split())
    text = patternRange.sub(r"\2", text)
    return text


def clean_ingredient_name(name):
    if not name:
        return ""
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9 \-']", "", name)
    name = " ".join(name.split())
    return name

#Convert the number given to a float number
def to_number(text):
    total = 0
    for part in text.split():
        if "/" in part:
            top, bottom = part.split("/")
            total += int(top) / int(bottom)
        else:
            total += float(part)
    return total


def try_to_number(text):
    try:
        return to_number(text)
    except ZeroDivisionError:
        return None


#to parse measurements given into a quantity, note and unit and handle crashes here
#if no quantity is giveb
def parse_measure(measure):
    measure = clean_text(measure)
    if not measure:
        return {"quantity": None, "unit": "", "note": ""}

    match = measurement.match(measure)
    if not match:
        return {"quantity": None, "unit": "", "note": measure}

    number_text, word, rest = match.groups()
    normalized_word = word.lower()

    quantity = try_to_number(number_text)
    if quantity is None:
        return {"quantity": None, "unit": "", "note": measure}

    if normalized_word in standardUnit:
        return {"quantity": quantity, "unit": standardUnit[normalized_word],
                "note": rest.lstrip(". ").strip()}

    return {"quantity": quantity, "unit": "", "note": (word + " " + rest).strip()}


def parse_ingredient_line(line):
    """Parse an ingredient line into quantity, unit, name and note."""
    line = clean_text(line)
    if not line:
        raise ValueError("Ingredient line is empty.")

    match = measurement.match(line)
    if match:
        number_text, word, rest = match.groups()
        normalized_word = word.lower()
        quantity = try_to_number(number_text)
        if quantity is None:
            raise ValueError(f"Invalid quantity in: '{line}'")
        if normalized_word in standardUnit:
            unit = standardUnit[normalized_word]
            text = rest.lstrip(". ")
        else:
            unit = ""
            text = word + " " + rest
    else:
        quantity, unit, text = None, "", line

    notes = re.findall(r"\(([^)]*)\)", text)
    text = re.sub(r"\([^)]*\)", "", text)
    if "," in text:
        text, after_comma = text.split(",", 1)
        notes.append(after_comma.strip())

    text = text.strip()
    if text.lower().startswith("of "):
        text = text[3:]
    name = clean_ingredient_name(text)
    if not name:
        raise ValueError(f"No ingredient name found in: '{line}'")

    return {"quantity": quantity, "unit": unit, "name": name,
            "note": ", ".join(n.strip() for n in notes if n.strip())}


def extract_ingredients(meal):
    ingredients = []
    for i in range(1, 21):
        name = clean_ingredient_name(meal.get(f"strIngredient{i}"))
        if not name:
            continue
        item = parse_measure(meal.get(f"strMeasure{i}"))
        item["name"] = name
        ingredients.append(item)

    if not ingredients:
        raise ValueError("No ingredients found for this meal.")
    return ingredients

#Here we check and convert quantities
def validate_quantity(value, allow_zero=False):
    if isinstance(value, bool):
        raise ValueError("Quantity must be a number.")

    if isinstance(value, (int, float)):
        number = float(value)
    else:
        text = clean_text(value)
        if not re.fullmatch(numbers, text):
            raise ValueError(f"'{value}' is not a valid number.")
        number = try_to_number(text)
        if number is None:
            raise ValueError(f"'{value}' is not a valid number.")

    if not math.isfinite(number):
        raise ValueError("Quantity must be a real number.")
    if number < 0 or (number == 0 and not allow_zero):
        raise ValueError("Quantity must be greater than zero.")
    return number


def validate_servings(text):
    text = str(text).strip()
    if not re.fullmatch(r"[1-9]\d?", text):
        raise ValueError("Servings must be a whole number from 1 to 99.")
    return int(text)


def scale_quantity(quantity, original_servings, new_servings):
    if original_servings <= 0 or new_servings <= 0:
        raise ValueError("Servings must be greater than zero.")
    if quantity is None:
        return None
    return round(quantity * new_servings / original_servings, 2)


if __name__ == "__main__":
    print("--- Raw ingredient lines ---")
    lines = ["2 tbsp butter", "1½ cups of flour (sifted)", "500g chicken breast, diced",
             "2-3 Tablespoons. olive oil", "salt", "3 eggs", "¼ tsp pepper"]
    for line in lines:
        print(repr(line), "->", parse_ingredient_line(line))

    print("--- TheMealDB measures ---")
    for m in ["1 1/2 cups", "500g", "1/2 tsp", "2 large", "Pinch", "", None, "1.5kg"]:
        print(repr(m), "->", parse_measure(m))

    print("--- validation ---")
    for item in ["2", "1 1/2", 0, "abc", "-3", "1/0", float("nan")]:
        try:
            print(repr(item), "->", validate_quantity(item))
        except ValueError as error:
            print(repr(item), "-> ERROR:", error)
    print(validate_servings("4"), scale_quantity(1.5, 4, 6))