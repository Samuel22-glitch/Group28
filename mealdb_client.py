import requests


class MealDBClient:
    """
    Handles communication with TheMealDB API.

    Responsibilities:
    - Search recipes by name
    - Search recipes by primary ingredient
    - Search recipes by category
    - Parse API responses
    - Handle network/API errors
    """

    BASE_URL = "https://www.themealdb.com/api/json/v1/1"

    def __init__(self):
        self.timeout = 10

    # ---------------------------------------------------------
    # 1. Search recipe by name
    # ---------------------------------------------------------
    def search_by_name(self, recipe_name):
        """Search for recipes using their name."""

        if not recipe_name or not recipe_name.strip():
            return []

        url = f"{self.BASE_URL}/search.php"

        try:
            response = requests.get(
                url,
                params={"s": recipe_name.strip()},
                timeout=self.timeout
            )

            response.raise_for_status()

            data = response.json()

            if not data or not data.get("meals"):
                return []

            return [
                self.parse_recipe(meal)
                for meal in data["meals"]
            ]

        except requests.exceptions.Timeout:
            print("Error: The request timed out.")
            return []

        except requests.exceptions.RequestException as error:
            print(f"Network error: {error}")
            return []

        except ValueError:
            print("Error: The API returned invalid JSON.")
            return []

    # ---------------------------------------------------------
    # 2. Search by primary ingredient
    # ---------------------------------------------------------
    def search_by_ingredient(self, ingredient):
        """Search recipes containing a specific ingredient."""

        if not ingredient or not ingredient.strip():
            return []

        url = f"{self.BASE_URL}/filter.php"

        try:
            response = requests.get(
                url,
                params={"i": ingredient.strip()},
                timeout=self.timeout
            )

            response.raise_for_status()

            data = response.json()

            if not data or not data.get("meals"):
                return []

            return [
                {
                    "id": meal.get("idMeal"),
                    "name": meal.get("strMeal"),
                    "thumbnail": meal.get("strMealThumb")
                }
                for meal in data["meals"]
            ]

        except requests.exceptions.Timeout:
            print("Error: The request timed out.")
            return []

        except requests.exceptions.RequestException as error:
            print(f"Network error: {error}")
            return []

        except ValueError:
            print("Error: The API returned invalid JSON.")
            return []

    # ---------------------------------------------------------
    # 3. Search by category
    # ---------------------------------------------------------
    def search_by_category(self, category):
        """Search recipes belonging to a category."""

        if not category or not category.strip():
            return []

        url = f"{self.BASE_URL}/filter.php"

        try:
            response = requests.get(
                url,
                params={"c": category.strip()},
                timeout=self.timeout
            )

            response.raise_for_status()

            data = response.json()

            if not data or not data.get("meals"):
                return []

            return [
                {
                    "id": meal.get("idMeal"),
                    "name": meal.get("strMeal"),
                    "thumbnail": meal.get("strMealThumb")
                }
                for meal in data["meals"]
            ]

        except requests.exceptions.Timeout:
            print("Error: The request timed out.")
            return []

        except requests.exceptions.RequestException as error:
            print(f"Network error: {error}")
            return []

        except ValueError:
            print("Error: The API returned invalid JSON.")
            return []

    # ---------------------------------------------------------
    # 4. Get complete recipe details
    # ---------------------------------------------------------
    def get_recipe(self, meal_id):
        """Get complete recipe information using its ID."""

        if not meal_id:
            return None

        url = f"{self.BASE_URL}/lookup.php"

        try:
            response = requests.get(
                url,
                params={"i": meal_id},
                timeout=self.timeout
            )

            response.raise_for_status()

            data = response.json()

            if not data or not data.get("meals"):
                return None

            return self.parse_recipe(data["meals"][0])

        except requests.exceptions.Timeout:
            print("Error: The request timed out.")
            return None

        except requests.exceptions.RequestException as error:
            print(f"Network error: {error}")
            return None

        except ValueError:
            print("Error: The API returned invalid JSON.")
            return None

    # ---------------------------------------------------------
    # 5. Parse raw API recipe data
    # ---------------------------------------------------------
    def parse_recipe(self, meal):
        """
        Convert raw TheMealDB JSON into a clean dictionary.
        """

        ingredients = []

        # TheMealDB stores ingredients in strIngredient1...
        # strIngredient20 and measurements in strMeasure1...
        for number in range(1, 21):

            ingredient = meal.get(f"strIngredient{number}")
            measure = meal.get(f"strMeasure{number}")

            if ingredient and ingredient.strip():

                ingredients.append({
                    "name": ingredient.strip(),
                    "measure": (measure or "").strip()
                })

        return {
            "id": meal.get("idMeal"),
            "name": meal.get("strMeal"),
            "category": meal.get("strCategory"),
            "cuisine": meal.get("strArea"),
            "instructions": meal.get("strInstructions"),
            "thumbnail": meal.get("strMealThumb"),
            "youtube":
     meal.get("strYoutube"),
            "ingredients": ingredients
        }