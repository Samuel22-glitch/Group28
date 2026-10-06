"""
Recipe scaling utilities.

This module converts ingredient quantities, scales recipes
for different serving sizes, and formats the results.
"""


# Common cooking units and their plural forms
UNIT_PLURALS = {
    "cup": "cups",
    "tablespoon": "tablespoons",
    "teaspoon": "teaspoons",
    "gram": "grams",
    "kilogram": "kilograms",
    "milliliter": "milliliters",
    "liter": "liters"
}


# Check that the serving sizes are valid
def validate_servings(original_servings, target_servings):
    """Validate the original and target serving sizes."""
    if original_servings <= 0:
        raise ValueError("Original servings must be greater than zero.")

    if target_servings <= 0:
        raise ValueError("Target servings must be greater than zero.")


# Check that an ingredient quantity is valid
def validate_quantity(quantity):
    """Validate an ingredient quantity."""
    if quantity <= 0:
        raise ValueError("Ingredient quantity must be greater than zero.")


# Calculate the new quantity based on servings
def scale_quantity(quantity, original_servings, target_servings):
    """Scale a quantity based on the number of servings."""
    validate_servings(original_servings, target_servings)
    validate_quantity(quantity)

    scale_factor = target_servings / original_servings

    return quantity * scale_factor


# Convert a fraction such as 1/2 into a decimal
def fraction_to_decimal(fraction):
    """Convert a fraction such as '1/2' into a decimal."""
    numerator, denominator = fraction.split("/")

    return float(numerator) / float(denominator)


# Convert an ingredient quantity into a number
def parse_quantity(quantity):
    """Convert a quantity into a decimal number."""
    try:
        if "/" in str(quantity):
            return fraction_to_decimal(quantity)

        return float(quantity)

    except (ValueError, ZeroDivisionError):
        raise ValueError(f"Invalid ingredient quantity: {quantity}")


# Remove unnecessary decimal places
def format_quantity(quantity):
    """Remove unnecessary decimal places from whole numbers."""
    if quantity.is_integer():
        return int(quantity)

    return quantity


# Choose the correct singular or plural unit
def format_unit(quantity, unit):
    """Return the correct singular or plural form of a unit."""
    if quantity == 1:
        return unit

    return UNIT_PLURALS.get(unit, f"{unit}s")


# Scale one ingredient
def scale_ingredient(quantity, unit, original_servings, target_servings):
    """Scale one ingredient and return its formatted quantity."""
    quantity = parse_quantity(quantity)

    scaled_quantity = scale_quantity(
        quantity,
        original_servings,
        target_servings
    )

    scaled_quantity = format_quantity(scaled_quantity)

    formatted_unit = format_unit(
        scaled_quantity,
        unit
    )

    return f"{scaled_quantity} {formatted_unit}"


# Scale all ingredients in a recipe
def scale_recipe(ingredients, original_servings, target_servings):
    """Scale all ingredients in a recipe."""
    scaled_ingredients = []

    for ingredient in ingredients:
        scaled_quantity = scale_ingredient(
            ingredient["quantity"],
            ingredient["unit"],
            original_servings,
            target_servings
        )

        scaled_ingredients.append({
            "name": ingredient["name"],
            "quantity": scaled_quantity
        })

    return scaled_ingredients


# Display the final scaled recipe
def display_recipe(ingredients):
    """Display the scaled ingredients in a readable format."""
    for ingredient in ingredients:
        print(f"{ingredient['name']}: {ingredient['quantity']}")

        # Main function for the rest of the project
def get_scaled_recipe(ingredients, original_servings, target_servings):
    """Return a complete scaled recipe."""
    return scale_recipe(
        ingredients,
        original_servings,
        target_servings
    )