
from pydantic import BaseModel
from typing import List
import json

class Ingredient(BaseModel):
    type: str = ""
    isCut: bool = False
    isTrash: bool = False
    isMixed: bool = False
    isFried: bool = False
    isDeepFried: bool = False
    isBurned: bool = False
    isBoiled: bool = False
    canCut: bool = False
    canMix: bool = False
    canFry: bool = False
    canDeepFry: bool = False
    canBoil: bool = False
    canBurn: bool = False
    name: str = ""

class VegetablesAndFruits(Ingredient):
    pass

class Proteins(Ingredient):
    cooked: bool = False

class BreadsAndBases(Ingredient):
    pass

class others(Ingredient):
    pass

def load_ingredients():         #funcion para cargar los ingredientes y traducirlos a una lista de python 
    with open ("components/ingredients.json") as file:
        data = json.load(file)
        return [Ingredient(**ingredient) for ingredient in data["Ingredients"]]