import json
import csv
import os


class ShoppingListGenerator:
    """
    Handles the generation, export, and import of meal plans
    and shopping lists.
    """

    def __init__(self, storage_directory="data"):
        self.storage_directory = storage_directory

        # Create the storage directory if it does not exist
        os.makedirs(self.storage_directory, exist_ok=True)

    def save_json(self, data, filename):
        """
        Save data to a JSON file.
        """
        filepath = os.path.join(self.storage_directory, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            return True

        except (TypeError, OSError) as error:
            print(f"Error saving JSON file: {error}")
            return False

    def load_json(self, filename):
        """
        Load data from a JSON file.
        """
        filepath = os.path.join(self.storage_directory, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                return json.load(file)

        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return None

        except json.JSONDecodeError:
            print(f"Invalid JSON file: {filepath}")
            return None

        except OSError as error:
            print(f"Error loading JSON file: {error}")
            return None

    def save_meal_plan(self, meal_plan, filename="meal_plan.json"):
        """
        Save a meal plan as JSON.
        """
        return self.save_json(meal_plan, filename)

    def save_shopping_list(self, shopping_list, filename="shopping_list.json"):
        """
        Save a shopping list as JSON.
        """
        return self.save_json(shopping_list, filename)

    def export_csv(self, data, filename="shopping_list.csv"):
        """
        Export shopping-list data to a CSV file.
        """

        filepath = os.path.join(self.storage_directory, filename)

        if not data:
            print("No data available to export.")
            return False

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as file:

                # If data is a list of dictionaries
                if isinstance(data, list) and isinstance(data[0], dict):

                    fieldnames = data[0].keys()

                    writer = csv.DictWriter(
                        file,
                        fieldnames=fieldnames
                    )

                    writer.writeheader()
                    writer.writerows(data)

                else:
                    print("CSV export requires a list of dictionaries.")
                    return False

            return True

        except OSError as error:
            print(f"Error exporting CSV: {error}")
            return False

    def load_meal_plan(self, filename="meal_plan.json"):
        """
        Restore a previously saved meal plan.
        """
        return self.load_json(filename)

    def load_shopping_list(self, filename="shopping_list.json"):
        """
        Restore a previously saved shopping list.
        """
        return self.load_json(filename)