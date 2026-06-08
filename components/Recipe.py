from pydantic import BaseModel
from typing import List
import json
from components.Ingredient import Ingredient


class RecipeIngredient(BaseModel):
    name: str = ""
    requiredState: List[str] = []
    
class Recipe(BaseModel):
    recipeId: str = ""
    name: str = ""
    requiredIngredients: List[RecipeIngredient] = []
    currentPoints: int = 0
    timeRemaining: float = 0.0
    canDeliver: bool = False

def load_recipes():
    with open ("recipes.json") as file:
        data = json.load(file)
        return [Recipe(**recipe) for recipe in data["recipes"]]
