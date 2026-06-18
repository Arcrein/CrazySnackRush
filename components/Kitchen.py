from datetime import datetime, time

from pydantic import BaseModel
from typing import List
from components.Orden import Orden
import components.Furniture as F 
import random
from components.Recipe import Recipe, load_recipes
from components.Ingredient import Ingredient, load_ingredients


def findRecipeByName(name: str, recipes: List[Recipe]):
    for recipe in recipes:
        if recipe.name == name:
            return recipe
    return None



class kitchen(BaseModel):
    name: str = ""
    type: str = ""
    state: str = ""
    furnitureList: List[F.Furniture] = []
    order_list: List[Orden] = []
    time_remaining: float = 0.0
    start_time: float = 0.0
    points: int = 0
    order_id_counter: int = 0
    remainingForOrder: float = 10.0
    
    def get_furniture(self, station_id: int):
        for furniture in self.furnitureList:
            if furniture.stationId == station_id:
                return furniture
        return None
    
    def getFurnitureByType(self, type: str):
        for furniture in self.furnitureList:
            if furniture.type == type:
                return furniture
        return None

    def getIngredient(self, name: str, ingredientList: List[Ingredient]):
        for ing in ingredientList:
            if ing.name == name:
                return ing
        return None
    
    def getOrder(self, order_id: int):
        for order in self.order_list:
            if order.id == order_id:
                return order
        return None

    def start_game(self, furnitures: List[F.Furniture], ingredientList: List[Ingredient], recipeOptions: List[str], recipes: List[Recipe]):
        self.time_remaining = 240.0
        self.start_time = datetime.now().timestamp()
        self.points = 0
        self.order_list.clear()
        self.furnitureList.clear()
        self.order_id_counter = 0
        self.remainingForOrder = 10.0

        self.generate_random_order(recipes, recipeOptions)
        self.generate_random_order(recipes, recipeOptions)
    
        for item in furnitures:
            print("Procesando item:", item.type, item.stationId)

            if item.type == "BunIngredientBox":
                nuevo = self.getIngredient("Bun", ingredientList)
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                self.furnitureList.append(box)
                print("ingrediente encontrado:", nuevo)

            if item.type == "MeatIngredientBox":
                nuevo = self.getIngredient("Meat", ingredientList)
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                self.furnitureList.append(box)

            if item.type == "LettuceIngredientBox":
                nuevo = self.getIngredient("Lettuce", ingredientList)
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                self.furnitureList.append(box)
            
            if item.type == "TomatoIngredientBox":
                nuevo = self.getIngredient("Tomato", ingredientList)
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                self.furnitureList.append(box)

            if item.type == "CheeseIngredientBox":
                nuevo = self.getIngredient("Cheese", ingredientList)
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                self.furnitureList.append(box)

            if item.type == "ChocolateIngredientBox":
                nuevo = self.getIngredient("Chocolate", ingredientList)
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                self.furnitureList.append(box)
            
            if item.type == "EggIngredientBox":
                nuevo = self.getIngredient("Egg", ingredientList)
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                self.furnitureList.append(box)
            
            if item.type == "FlourIngredientBox":
                nuevo = self.getIngredient("Flour", ingredientList)
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                self.furnitureList.append(box)

            if item.type == "NoriIngredientBox":
                nuevo = self.getIngredient("Nori", ingredientList)
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                self.furnitureList.append(box)

            if item.type == "RiceIngredientBox":
                nuevo = self.getIngredient("Rice", ingredientList)
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                self.furnitureList.append(box)
            
            if item.type == "CuecumberIngredientBox":
                nuevo = self.getIngredient("Cucumber", ingredientList)
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                self.furnitureList.append(box)

            if item.type == "FishIngredientBox":
                nuevo = self.getIngredient("Fish", ingredientList)
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                self.furnitureList.append(box)
            
            if item.type == "CuttingTable":
                box = F.cuttingBoard(
                    stationId=item.stationId,
                    type=item.type,
                    held=item.held
                )
                self.furnitureList.append(box)
            
            if item.type == "Table":
                box = F.table(
                    stationId=item.stationId,
                    type=item.type,
                    held=item.held
                )
                self.furnitureList.append(box)
            
            if item.type == "Stove":
                box = F.stove(
                    stationId=item.stationId,
                    type=item.type,
                    held=item.held
                )
                self.furnitureList.append(box)

            if item.type == "ServingStation":
                box = F.servingStation(
                    stationId=item.stationId,
                    type=item.type,
                    held=item.held
                )
                self.furnitureList.append(box)

            if item.type == "TrashCan":     
                box = F.trashCan(
                    stationId=item.stationId,
                    type=item.type,
                    held=item.held
                )
                self.furnitureList.append(box)
            
            if item.type == "DishSpawner":
                box = F.dishSpawner(
                    stationId=item.stationId,
                    type=item.type,
                    held=item.held
                )
                self.furnitureList.append(box)
            
            if item.type == "Sink":
                box = F.sink(
                    stationId=item.stationId,
                    type=item.type,
                    held=item.held
                )
                self.furnitureList.append(box)

    def update_time(self, ingredientList: List[Ingredient], recipeOptions: List[str], recipes: List[Recipe]):
        now_ts = datetime.now().timestamp()
        delta_time = now_ts - self.start_time
        self.time_remaining -= delta_time
        for furniture in self.furnitureList:
            furniture.sync(ingredientList)
        for order in self.order_list:
            if order.status == False:
                order.time_remaining -= now_ts - order.start_time
                order.start_time = now_ts
                if order.time_remaining <= 0:
                    self.points -= 30
                    order.status = True #se marca como orden fallida
            else:
                order.start_time = now_ts #si la orden ya fue fallida, solo se actualiza el start_time para que no siga descontando tiempo
                order.time_remaining = 120.0 #y se asegura que el tiempo restante sea 2 min
        #se generan nuevas ordenes si es necesario cada 10 segundos
        self.remainingForOrder -= delta_time
        if self.remainingForOrder <= 0:
            self.remainingForOrder = 10.0
            self.generate_random_order(recipes, recipeOptions)
        self.start_time = now_ts
   
    def complete_order(self, order: Orden):
        order_in_list = self.getOrder(order.id)
        if order_in_list and order_in_list.status == False:
            dishSpawner: F.dishSpawner = self.getFurnitureByType("DishSpawner")
            if dishSpawner:
                dishSpawner.deliverPlate()
            self.points += order_in_list.recipe.currentPoints
            if order_in_list.time_remaining > 80.0:
                self.points += 8 #puntos extra por completar la orden a tiempo
            elif order_in_list.time_remaining > 40.0:
                self.points += 5
            else:
                self.points += 3
            order.status = True #se marca como orden completada
            self.order_list.remove(order) #se remueve la orden de la lista

    def generate_random_order(self, recipes: List[Recipe], recipeOptions: List[str]):
        if len(self.order_list) < 5: #si hay menos de 5ordenes, se genera una nueva orden
            random_recipe = random.choice(recipeOptions)
            found_recipe = findRecipeByName(random_recipe, recipes)
            self.order_id_counter += 1
            new_order = Orden(id=self.order_id_counter, recipe=found_recipe, status=False, time_remaining=120.0, start_time=datetime.now().timestamp())
            self.order_list.append(new_order)
        
