from pydantic import BaseModel, Field
from typing import List
import json
from components.core import IngredientDto

class RecipeIngredient(BaseModel):
    name: str = ""
    requiredState: List[str] = Field(default_factory=list)
    
class Recipe(BaseModel):
    recipeId: str = ""
    orderId: int = 0
    name: str = ""
    requiredIngredients: List[RecipeIngredient] = Field(default_factory=list)
    currentPoints: int = 0
    timeRemaining: float = 120.0
    canDeliver: bool = False

    @staticmethod
    def ingredientMatchesRequirement(ingredient: IngredientDto, requirement: RecipeIngredient) -> bool:
        ingredient_name = ingredient.name.lower()
        requirement_name = requirement.name.lower()

        if requirement_name not in ingredient_name:
            return False

        if len(requirement.requiredState) == 0:
            return True

        return ingredient.state in requirement.requiredState


    def recipeMatchesIngredients(self, ingredients: List[IngredientDto]) -> bool:
        if len(ingredients) > len(self.requiredIngredients):
            return False

        used_requirements = [False] * len(self.requiredIngredients)

        def backtrack(index: int) -> bool:
            if index >= len(ingredients):
                return True

            ingredient = ingredients[index]

            for req_index, requirement in enumerate(self.requiredIngredients):
                if used_requirements[req_index]:
                    continue
                if not self.ingredientMatchesRequirement(ingredient, requirement):
                    continue

                used_requirements[req_index] = True
                if backtrack(index + 1):
                    return True
                used_requirements[req_index] = False

            return False

        return backtrack(0)


def find_matching_recipes(ingredients: List[IngredientDto], recipes: List[Recipe], deliverable_only: bool = True) -> List[Recipe]:
    matching_recipes: List[Recipe] = []

    for recipe in recipes:
        if deliverable_only and not recipe.canDeliver:
            continue
        if recipe.recipeMatchesIngredients(ingredients):
            matching_recipes.append(recipe)

    return matching_recipes


def load_recipes():
    with open ("components/recipes.json") as file:
        data = json.load(file)
        return [Recipe(**recipe) for recipe in data["recipes"]]
