from datetime import datetime, time

from pydantic import BaseModel
from typing import List
from components.Orden import Orden
import components.Furniture as F 
import random
from components.Recipe import load_recipes
from components.Ingredient import Ingredient, load_ingredients

class kitchen(BaseModel):
    name: str = ""
    type: str = ""
    state: str = ""
    furnitureList: List[F.Furniture] = []
    order_list: List[Orden] = []
    time_remaining: float = 0.0
    start_time: float = 0.0
    points: int = 0
    
    def get_furniture(self, station_id: int):
        for furniture in self.furnitureList:
            if furniture.stationId == station_id:
                return furniture
        return None
    

    def start_game(self):
        self.time_remaining = 240.0
        self.start_time = datetime.now().timestamp()
        self.points = 0
        self.order_list.clear()
        self.furnitureList.clear()

    def update_time(self, ingredientList: List[Ingredient]):
        now_ts = datetime.now().timestamp()
        self.time_remaining -= now_ts - self.start_time
        self.start_time = now_ts
        for furniture in self.furnitureList:
            furniture.sync(ingredientList)
   

    def generate_random_order(self):
        recipes = load_recipes()
        if len(self.order_list) == 0 and self.time_remaining > 40: #si no hay ordenes y el tiempo resante es mayor a 40 segundos, se genera una nueva orden
            random_recipe = random.choice(recipes)
            new_order = Orden(recipe=random_recipe, status=False)
            self.order_list.append(new_order)
        elif len(self.order_list) != 0 and len(self.order_list) < 5 and self.time_remaining > 40: #si hay ordenes, pero no mas de 4 y el tiempo restante es mayor a 40 segundos, genera una nueva orden cada 50 segundos
            if int(self.time_remaining) % 50 == 0:
                random_recipe = random.choice(recipes)
                new_order = Orden(recipe=random_recipe, status=False)
                self.order_list.append(new_order)
        