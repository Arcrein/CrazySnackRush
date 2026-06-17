from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
from components.Kitchen import kitchen
import components.Furniture as F 
import components.Ingredient as I
from components.Recipe import Recipe, load_recipes
import asyncio
import time
from components.Ingredient import Ingredient, load_ingredients

class kitchenStartRequest(BaseModel):
    furnitures: List[F.Furniture] = []
    
class SimpleResponse(BaseModel):
    bSuccess: bool
    Message: str

class GameState:
    def __init__(self):
        self.kitchen = kitchen()
        self.ingredientList = load_ingredients()
        self.recipeList = load_recipes()
        self.lock = asyncio.Lock()

    def getIngredient(self, name: str):
        for ing in self.ingredientList:
            if ing.name == name:
                return ing
        return None
        
@asynccontextmanager
async def lifeSpan(app:FastAPI):
    app.state.game = GameState()
    yield
    app.state.game = None

app = FastAPI(lifespan=lifeSpan)

@app.post("/game/start", response_model=SimpleResponse)
async def gameStart(data: kitchenStartRequest, request: Request):
    game: GameState = request.app.state.game
    async with game.lock:
        game.kitchen.start_game()

        for item in data.furnitures:
            print("Procesando item:", item.type, item.stationId)

            if item.type == "BunIngredientBox":
                nuevo = game.getIngredient("Bun")
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                game.kitchen.furnitureList.append(box)
                print("ingrediente encontrado:", nuevo)

            if item.type == "MeatIngredientBox":
                nuevo = game.getIngredient("Meat")
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                game.kitchen.furnitureList.append(box)
            
            if item.type == "LettuceIngredientBox":
                nuevo = game.getIngredient("Lettuce")
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                game.kitchen.furnitureList.append(box)
            
            if item.type == "TomatoIngredientBox":
                nuevo = game.getIngredient("Tomato")
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                game.kitchen.furnitureList.append(box)

            if item.type == "CheeseIngredientBox":
                nuevo = game.getIngredient("Cheese")
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                game.kitchen.furnitureList.append(box)
            
            if item.type == "CuttingTable":
                box = F.cuttingBoard(
                    stationId=item.stationId,
                    type=item.type,
                    held=item.held
                )
                game.kitchen.furnitureList.append(box)
            
            if item.type == "Table":
                box = F.table(
                    stationId=item.stationId,
                    type=item.type,
                    held=item.held
                )
                game.kitchen.furnitureList.append(box)
            
            if item.type == "Stove":
                box = F.stove(
                    stationId=item.stationId,
                    type=item.type,
                    held=item.held
                )
                game.kitchen.furnitureList.append(box)

    return SimpleResponse(bSuccess=True, Message="ok")

@app.post("/game/interact", response_model=F.InteractResponse)
async def interact_with_station(data: F.InteractRequest, request: Request):
    game: GameState = request.app.state.game
    async with game.lock:

        station = game.kitchen.get_furniture(data.stationId)

        if station is not None:
            response = station.doInteract(data, game.ingredientList, game.recipeList)
            return response

    return F.InteractResponse(
        bSuccess=False,
        Message="La estación no tiene una acción válida.",
        Score=0,
        UpdatedHeld=data.held,
        ActiveRecipes=[]
    )

@app.get("/game/interact", response_model=kitchen)
async def getKitchenState(request: Request):
    game: GameState = request.app.state.game
    async with game.lock:
            game.kitchen.update_time(game.ingredientList)
            return game.kitchen
