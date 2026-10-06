from parser import validate_servings, scale_quantity

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SLOTS = ["breakfast", "lunch", "dinner"]
DEFAULT_SERVINGS = 4
TO_BASE_UNIT = {"kg": ("g", 1000), "l": ("ml", 1000)}


class MealPlanner:
    def __init__(self):
        self.plan = {day: {slot: None for slot in SLOTS} for day in DAYS}

    def _find(self, day, slot):
        day, slot = day.strip().title(), slot.strip().lower()
        if day not in self.plan or slot not in SLOTS:
            raise ValueError(f"Unknown day or slot: '{day}' '{slot}'")
        return self.plan[day], slot

    def add_recipe(self, day, slot, recipe, servings=None):
        meals, slot = self._find(day, slot)
        if not recipe.get("name") or not recipe.get("ingredients"):
            raise ValueError("A recipe needs a name and ingredients.")
        if meals[slot] is not None:
            raise ValueError(f"{day} {slot} is taken. Use update_recipe() or remove_recipe().")
        if servings is None:
            servings = recipe.get("servings", DEFAULT_SERVINGS)
        meals[slot] = {"recipe": recipe, "servings": validate_servings(servings)}

    def update_recipe(self, day, slot, recipe=None, servings=None):
        meals, slot = self._find(day, slot)
        if meals[slot] is None:
            raise ValueError(f"{day} {slot} is empty. Use add_recipe().")
        if servings is None:
            servings = meals[slot]["servings"]
        meals[slot] = {"recipe": recipe or meals[slot]["recipe"],
                       "servings": validate_servings(servings)}

    def remove_recipe(self, day, slot):
        meals, slot = self._find(day, slot)
        if meals[slot] is None:
            raise ValueError(f"{day} {slot} is already empty.")
        name = meals[slot]["recipe"]["name"]
        meals[slot] = None
        return name

    def get_shopping_list(self):
        totals = {}
        for meals in self.plan.values():
            for entry in meals.values():
                if entry is None:
                    continue
                recipe = entry["recipe"]
                original = recipe.get("servings", DEFAULT_SERVINGS)
                for item in recipe["ingredients"]:
                    quantity = scale_quantity(item["quantity"], original, entry["servings"])
                    unit = item["unit"]
                    if quantity is not None and unit in TO_BASE_UNIT:
                        unit, factor = TO_BASE_UNIT[unit]
                        quantity *= factor
                    key = (item["name"], unit)
                    total = totals.get(key)
                    if quantity is not None:
                        total = (total or 0) + quantity
                    totals[key] = total

        return [{"name": name, "unit": unit,
                 "quantity": None if total is None else round(total, 2)}
                for (name, unit), total in sorted(totals.items())]


if __name__ == "__main__":
    pancakes = {"name": "Pancakes", "servings": 4, "ingredients": [
        {"quantity": 300.0, "unit": "g", "name": "flour"},
        {"quantity": 2.0, "unit": "", "name": "eggs"},
        {"quantity": None, "unit": "", "name": "salt"}]}
    omelette = {"name": "Omelette", "servings": 2, "ingredients": [
        {"quantity": 3.0, "unit": "", "name": "eggs"},
        {"quantity": 1.0, "unit": "tbsp", "name": "butter"},
        {"quantity": None, "unit": "", "name": "salt"}]}
    bread = {"name": "Bread", "servings": 4, "ingredients": [
        {"quantity": 0.8, "unit": "kg", "name": "flour"}]}

    planner = MealPlanner()
    planner.add_recipe("monday", "breakfast", pancakes)
    planner.add_recipe("Tuesday", "breakfast", omelette)
    planner.add_recipe("Wednesday", "dinner", bread, servings=8)
    for item in planner.get_shopping_list():
        print(item)

    print("-- update Tuesday to 4 servings, remove Monday --")
    planner.update_recipe("Tuesday", "breakfast", servings=4)
    print("Removed:", planner.remove_recipe("Monday", "breakfast"))
    for item in planner.get_shopping_list():
        print(item)

    print("-- errors --")
    for action in [lambda: planner.add_recipe("Tuesday", "breakfast", omelette),
                   lambda: planner.add_recipe("Funday", "lunch", omelette),
                   lambda: planner.update_recipe("Friday", "lunch", servings=2),
                   lambda: planner.remove_recipe("Friday", "lunch"),
                   lambda: planner.add_recipe("Friday", "lunch", omelette, servings="abc")]:
        try:
            action()
        except ValueError as error:
            print("ERROR:", error)