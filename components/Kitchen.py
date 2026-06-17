from pydantic import BaseModel
from typing import List
from components.Orden import Orden
import components.Furniture as F 
import random
from components.Recipe import load_recipes

class kitchen(BaseModel):
    name: str = ""
    type: str = ""
    state: str = ""
    furnitureList: List[F.Furniture] = []
    order_list: List[Orden] = []
    time_remaining: float = 0.0
    points: int = 0

def generate_random_order(kitchen: kitchen):
    recipes = load_recipes()
    if len(kitchen.order_list) == 0 and kitchen.time_remaining > 40: #si no hay ordenes y el tiempo resante es mayor a 40 segundos, se genera una nueva orden
        random_recipe = random.choice(recipes)
        new_order = Orden(recipe=random_recipe, status=False)
        kitchen.order_list.append(new_order)
    elif len(kitchen.order_list) != 0 and len(kitchen.order_list) < 5 and kitchen.time_remaining > 40: #si hay ordenes, pero no mas de 4 y el tiempo restante es mayor a 40 segundos, genera una nueva orden cada 50 segundos
        if int(kitchen.time_remaining) % 50 == 0:
            random_recipe = random.choice(recipes)
            new_order = Orden(recipe=random_recipe, status=False)
            kitchen.order_list.append(new_order)
        