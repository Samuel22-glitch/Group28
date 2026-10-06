import streamlit as st
from mealplanner import MealPlanner

from mealdb_client import MealDBClient


# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Recipe & Smart Meal Planner",
    page_icon="🍽️",
    layout="wide"
)


# ---------------- API CLIENT ----------------

mealdb = MealDBClient()
planner = MealPlanner()

try:
    from gemini_client import GeminiClient
    gemini = GeminiClient()
except Exception:
    class GeminiFallback:
        def ask(self, prompt):
            return (
                "Gemini is not configured yet. Please add the AI client "
                "integration and API key to enable the assistant."
            )

    gemini = GeminiFallback()

# ---------------- SESSION STATE ----------------

if "recipes" not in st.session_state:
    st.session_state.recipes = []

if "meal_plan" not in st.session_state:
    st.session_state.meal_plan = {
        "Monday": [],
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
        "Friday": [],
        "Saturday": [],
        "Sunday": []
    }

if "shopping_list" not in st.session_state:
    st.session_state.shopping_list = []

if "ai_result" not in st.session_state:
    st.session_state.ai_result = ""


# ---------------- HEADER ----------------

st.title("🍽️ Recipe & Smart Meal Planner")

st.write(
    "Discover recipes, plan meals, manage ingredients, "
    "adjust serving sizes and create shopping lists."
)


# ---------------- SIDEBAR ----------------

st.sidebar.title("📌 Menu")

page = st.sidebar.radio(
    "Navigate to:",
    [
        "Recipe Discovery",
        "Meal Planner",
        "Shopping List",
        "AI Assistant",
        "Serving Control",
        "Export & Save"
    ]
)

st.sidebar.divider()

st.sidebar.info("Group 28 • Recipe & Smart Meal Planner")


# ==========================================================
# 1. RECIPE DISCOVERY
# ==========================================================

if page == "Recipe Discovery":

    st.header("🔎 Recipe Discovery")

    st.write(
        "Search for recipes by name, ingredient or category."
    )

    col1, col2 = st.columns([3, 1])

    with col1:

        search_type = st.selectbox(
            "Search By",
            [
                "Recipe Name",
                "Ingredient",
                "Category"
            ]
        )

    with col2:

        category = st.selectbox(
            "Category Filter",
            [
                "All",
                "Chicken",
                "Beef",
                "Dessert",
                "Vegetarian",
                "Seafood"
            ]
        )

    search_term = st.text_input(
        "Search Recipe",
        placeholder="e.g. chicken, rice, pasta..."
    )

    if st.button("🔍 Search Recipes", type="primary"):

        if not search_term.strip():

            st.warning("Please enter something to search for.")

        else:

            with st.spinner("Searching TheMealDB..."):

                if search_type == "Recipe Name":

                    results = mealdb.search_by_name(search_term)

                elif search_type == "Ingredient":

                    results = mealdb.search_by_ingredient(search_term)

                else:

                    results = mealdb.search_by_category(search_term)

            # Apply category filter when appropriate
            if category != "All":

                results = [
                    recipe
                    for recipe in results
                    if recipe.get("category") == category
                ]

            st.session_state.recipes = results

    # ---------------- DISPLAY RESULTS ----------------

    if st.session_state.recipes:

        st.subheader("Available Recipes")

        for index, recipe in enumerate(st.session_state.recipes):

            with st.container(border=True):

                left, right = st.columns([4, 1])

                with left:

                    st.subheader(
                        recipe.get("name", "Unknown Recipe")
                    )

                    if recipe.get("thumbnail"):

                        st.image(
                            recipe["thumbnail"],
                            width=250
                        )

                    if recipe.get("category"):

                        st.write(
                            f"**Category:** {recipe['category']}"
                        )

                    if recipe.get("cuisine"):

                        st.write(
                            f"**Cuisine:** {recipe['cuisine']}"
                        )

                    ingredients = recipe.get("ingredients", [])

                    if ingredients:

                        ingredient_text = ", ".join(
                            [
                                f"{item['measure']} {item['name']}".strip()
                                for item in ingredients
                            ]
                        )

                        st.write(
                            f"**Ingredients:** {ingredient_text}"
                        )

                    with st.expander("View Instructions"):

                        st.write(
                            recipe.get(
                                "instructions",
                                "No instructions available."
                            )
                        )

                    if recipe.get("youtube"):

                        st.link_button(
                            "▶️ Watch Recipe Video",
                            recipe["youtube"]
                        )

                with right:

                    selected_day = st.selectbox(
                        "Add to",
                        list(st.session_state.meal_plan.keys()),
                        key=f"day_{index}_{recipe.get('id')}"
                    )

                    if st.button(
                        "➕ Add",
                        key=f"add_{index}_{recipe.get('id')}"
                    ):

                        st.session_state.meal_plan[
                            selected_day
                        ].append(recipe)

                        st.success(
                            f"Added to {selected_day}"
                        )

    elif search_term and st.session_state.recipes == []:

        st.info("No recipes found.")


# ==========================================================
# 2. MEAL PLANNER
# ==========================================================

elif page == "Meal Planner":

    st.header("📅 Meal Planner")

    st.write(
        "Organize your selected recipes across the week."
    )

    for day, meals in st.session_state.meal_plan.items():

        with st.expander(day):

            if meals:

                for index, meal in enumerate(meals):

                    col1, col2 = st.columns([5, 1])

                    with col1:

                        st.write(
                            f"🍴 {meal.get('name', 'Unknown Recipe')}"
                        )

                    with col2:

                        if st.button(
                            "Remove",
                            key=f"remove_{day}_{index}"
                        ):

                            st.session_state.meal_plan[
                                day
                            ].pop(index)

                            st.rerun()

            else:

                st.caption(
                    "No meals planned for this day."
                )


# ==========================================================
# 3. SHOPPING LIST
# ==========================================================

elif page == "Shopping List":

    st.header("🛒 Consolidated Shopping List")

    st.write(
        "Ingredients from planned meals will appear here."
    )

    ingredient_count = {}

    for day, meals in st.session_state.meal_plan.items():

        for meal in meals:

            for ingredient in meal.get("ingredients", []):

                name = ingredient.get("name", "").strip().lower()

                measure = ingredient.get(
                    "measure",
                    ""
                ).strip()

                if not name:
                    continue

                if name not in ingredient_count:

                    ingredient_count[name] = {
                        "name": name,
                        "measures": []
                    }

                if measure:

                    ingredient_count[name]["measures"].append(
                        measure
                    )

    if ingredient_count:

        shopping_rows = []

        for item in ingredient_count.values():

            shopping_rows.append(
                {
                    "Ingredient": item["name"].title(),
                    "Quantity": ", ".join(item["measures"])
                    if item["measures"]
                    else "As needed"
                }
            )

        st.session_state.shopping_list = shopping_rows

        st.dataframe(
            shopping_rows,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Add recipes to your meal plan first."
        )


# ==========================================================
# 4. AI ASSISTANT
# ==========================================================

elif page == "AI Assistant":

    st.header("🤖 AI Assistant")

    st.write(
        "Ask Gemini for recipe instructions, "
        "ingredient substitutions, cooking tips and meal ideas."
    )

    request = st.text_area(
        "What would you like help with?",
        placeholder=(
            "Example: What can I use instead of tomatoes?"
        )
    )

    if st.button("✨ Ask AI", type="primary"):

        if not request.strip():

            st.warning("Please enter a request.")

        else:

            with st.spinner("Gemini is thinking..."):

                answer = gemini.ask(request)

            st.session_state.ai_result = answer

    if st.session_state.ai_result:

        st.subheader("🤖 Gemini's Response")

        st.write(
            st.session_state.ai_result
        )

# ==========================================================
# 5. SERVING CONTROL
# ==========================================================

elif page == "Serving Control":

    st.header("⚖️ Serving & Portion Control")

    st.write(
        "Adjust recipe quantities based on the desired "
        "number of servings."
    )

    current_servings = st.number_input(
        "Current Servings",
        min_value=1,
        value=4
    )

    target_servings = st.number_input(
        "Target Servings",
        min_value=1,
        value=6
    )

    if st.button(
        "Calculate Scaling",
        type="primary"
    ):

        scaling_factor = (
            target_servings / current_servings
        )

        st.metric(
            "Scaling Factor",
            f"{scaling_factor:.2f}x"
        )

        st.info(
            "Recipe quantities will be scaled using "
            "the portion-scaling module."
        )


# ==========================================================
# 6. EXPORT & SAVE
# ==========================================================

elif page == "Export & Save":

    st.header("💾 Export & Save")

    st.write(
        "Export your meal plan and shopping list."
    )

    meal_plan_text = ""

    for day, meals in st.session_state.meal_plan.items():

        if meals:

            meal_text = ", ".join(
                meal.get("name", "Unknown Recipe")
                for meal in meals
            )

        else:

            meal_text = "No meals"

        meal_plan_text += (
            f"{day}: {meal_text}\n"
        )

    st.download_button(
        "⬇️ Download Meal Plan",
        data=meal_plan_text,
        file_name="meal_plan.txt",
        mime="text/plain"
    )

    if st.session_state.shopping_list:

        csv_data = "Ingredient,Quantity\n"

        for row in st.session_state.shopping_list:

            csv_data += (
                f"{row['Ingredient']},"
                f"{row['Quantity']}\n"
            )

        st.download_button(
            "⬇️ Download Shopping List CSV",
            data=csv_data,
            file_name="shopping_list.csv",
            mime="text/csv"
        )

    else:

        st.info(
            "Generate your shopping list first."
        )


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "Group 28 | Recipe & Smart Meal Planner"
)