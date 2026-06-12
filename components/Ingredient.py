
from pydantic import BaseModel
from typing import List
import json
from components.core import IngredientDto

class Ingredient(BaseModel):
    state: str = ""
    type: str = ""
    isReady: bool = False
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
    cutResult: str = ""
    mixResult: str = ""
    fryResult: str = ""
    deepFryResult: str = ""
    boilResult: str = ""
    burnResult: str = ""
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
