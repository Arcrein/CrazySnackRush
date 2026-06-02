from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

class RecipeIngredient(BaseModel):
    name: str = ""
    requiredState: List[str] = []
    
class Recipe(BaseModel):
    recipeId: str = ""
    name: str = ""
    requiredIngredients: List[RecipeIngredient] = []
    currentPoints: int = 0
    timeRemaining: float = 0.0

def getRecepies():
    ingredient1 = RecipeIngredient(name = "Meat", requiredState= ["Cut","Fried"])
    ingredient2 = RecipeIngredient(name = "Pan")