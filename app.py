import streamlit as st

from parse import parse_ingredient_line, scale_quantity, validate_quantity

st.set_page_config(page_title="Recipe Ingredient Cleaner")
st.title("Recipe Ingredient Cleaner")
st.write("Enter one ingredient per line.")

ingredients = st.text_area(
    "Ingredients",
    "2 tbsp butter\n1½ cups flour (sifted)\n500g chicken breast, diced\nsalt",
)
col1, col2 = st.columns(2)
original_servings = col1.number_input("Original servings", 1, 99, 4)
new_servings = col2.number_input("Scale to servings", 1, 99, 4)

if st.button("Clean ingredients"):
    results = []

    for line_number, line in enumerate(ingredients.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = parse_ingredient_line(line)
            quantity = item["quantity"]
            if quantity is not None:
                quantity = validate_quantity(quantity)
                item["quantity"] = scale_quantity(
                    quantity, original_servings, new_servings
                )
            results.append(item)
        except ValueError as error:
            st.error(f"Line {line_number}: {error} ({line})")

    if results:
        st.dataframe(results, hide_index=True, use_container_width=True)
    elif not ingredients.strip():
        st.info("Enter at least one ingredient.")
