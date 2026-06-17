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
from components.Recipe import load_recipes, load_ingredients

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
        
@asynccontextmanager
async def lifeSpan(app:FastAPI):
    app.state.game = GameState()
    yield
    app.state.game = None

app = FastAPI(lifespan=lifeSpan)

def find_ingredient(name: str):
    all_ingredients = load_ingredients()
    ingredient_data = next((i for i in all_ingredients if i.name == name), None)
    return ingredient_data

@app.post("/game/start", response_model=SimpleResponse)
async def gameStart(data: kitchenStartRequest, request: Request):
    game: GameState = request.app.state.game
    async with game.lock: 
        for item in data.furnitures:
            if item.type == "BunIngredientBox":
                game.kitchen.furnitureList.append(F.IngredientBox(stationId=item.stationId, type=item.type, contains=I.Ingredient(
                    isCut=False, isTrash=False, isMixed=False, isFried=False,
                    isDeepFried=False, isBoiled=False, canCut=False, canMix=False,
                    canFry=False, canDeepFry=False, canBoil=False, name="Bun"
                )))
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
