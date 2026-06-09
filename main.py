from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
from components.Kitchen import kitchen
import components.Furniture as F 
import components.Ingredient as I
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
        self.kitchen.ingredientList = load_ingredients()
        self.lock = asyncio.Lock()
        
@asynccontextmanager
async def lifeSpan(app:FastAPI):
    app.state.game = GameState()
    yield
    app.state.game = None

app = FastAPI(lifespan=lifeSpan)

@app.post("/game/start", response_model=SimpleResponse)
@app.post("/game/start", response_model=SimpleResponse)
async def gameStart(data: kitchenStartRequest, request: Request):
    game: GameState = request.app.state.game
    async with game.lock:
        print("=== GAME START ===")
        print("furnitures recibidos:", [(x.type, x.stationId) for x in data.furnitures])

        game.kitchen.furnitureList.clear()

        for item in data.furnitures:
            print("Procesando item:", item.type, item.stationId)

            if item.type == "BunIngredientBox":
                nuevo = game.kitchen.getIngredient("Bun")
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                game.kitchen.furnitureList.append(box)
                print("Agregada caja Bun:", box.stationId, box.type, box.contains.name)

            if item.type == "MeatIngredientBox":
                nuevo = game.kitchen.getIngredient("Meat")
                box = F.IngredientBox(
                    stationId=item.stationId,
                    type=item.type,
                    contains=nuevo
                )
                game.kitchen.furnitureList.append(box)
                print("Agregada caja Meat:", box.stationId, box.type, box.contains.name)

        print("LISTA FINAL START:",
              [(f.type, f.stationId, f.contains.name) for f in game.kitchen.furnitureList])

    return SimpleResponse(bSuccess=True, Message="ok")

@app.post("/game/interact", response_model=F.InteractResponse)
@app.post("/game/interact", response_model=F.InteractResponse)
async def interact_with_station(data: F.InteractRequest, request: Request):
    game: GameState = request.app.state.game
    async with game.lock:
        print("=== INTERACT ===")
        print("stationId recibido:", data.stationId)
        print("held recibido:", data.held)

        print("LISTA ACTUAL:",
              [(f.type, f.stationId, f.contains.name) for f in game.kitchen.furnitureList])

        station = game.kitchen.get_furniture(data.stationId)
        print("station encontrada:", station)

        if station is not None:
            response = station.doInteract(data)
            print("respuesta:", response)
            return response

    print("NO SE ENCONTRO STATION PARA:", data.stationId)
    return F.InteractResponse(
        bSuccess=False,
        Message="La estación no tiene una acción válida.",
        Score=0,
        UpdatedHeld=data.held,
        ActiveRecipes=[]
    )