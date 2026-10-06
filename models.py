class Recipe:
    """
    Base Recipe model for the Recipe & Smart Meal Planner.
    This class will help connect the different team modules.
    """

    def __init__(
        self,
        name,
        category,
        ingredients,
        servings=1,
        instructions=""
    ):

        self.name = name
        self.category = category
        self.ingredients = ingredients
        self.servings = servings
        self.instructions = instructions

    def to_dict(self):

        return {
            "name": self.name,
            "category": self.category,
            "ingredients": self.ingredients,
            "servings": self.servings,
            "instructions": self.instructions
        }