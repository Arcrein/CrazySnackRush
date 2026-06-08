from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
from components.Kitchen import kitchen
import components.Furniture as F 
import components.Ingredient as I
import asyncio
import time




class IngredientDto(BaseModel):
    name: str = ""
    type: str = ""
    state: str = ""


class RecipeDto(BaseModel):
    RecipeId: str = ""
    Name: str = ""
    RequiredIngredients: List[IngredientDto] = []
    CurrentPoints: int = 0
    TimeRemaining: float = 0.0

class kitchenStartRequest(BaseModel):
    furnitures: List[F.Furniture] = []
    
class SimpleResponse(BaseModel):
    bSuccess: bool
    Message: str

class InteractRequest(BaseModel):
    chefId: int
    stationId: int
    action: str
    heldIngredient: IngredientDto


class InteractResponse(BaseModel):
    bSuccess: bool
    Message: str
    Score: int
    UpdatedHeldIngredient: IngredientDto
    ActiveRecipes: List[RecipeDto]


class GameState:
    def __init__(self):
        self.kitchen = kitchen()
        self.lock = asyncio.Lock()
        
@asynccontextmanager
async def lifeSpan(app:FastAPI):
    app.state.game = GameState()
    yield
    app.state.game = None

app = FastAPI(lifespan=lifeSpan)

@app.post("/game/start", response_model=SimpleResponse)
async def gameStart(data: kitchenStartRequest, request: Request):
    game: GameState  = request.app.state.game
    async with game.lock: 
        game.kitchen.furnitureList.clear()
        for item in data.furnitures:
            if item.type == "BunIngredientBox":
                game.kitchen.furnitureList.append(F.IngredientBox(stationId=item.stationId, type=item.type, contains=I.Ingredient(
                    isCut= False,
                    isTrash= False,
                    isMixed= False,
                    isFried= False,
                    isDeepFried= False,
                    isBoiled= False,
                    canCut= False,
                    canMix= False,
                    canFry= False,
                    canDeepFry= False,
                    canBoil= False,
                    name= "Bun"
                )))
    return SimpleResponse(bSuccess=True, Message="ok")

@app.post("/game/interact", response_model=InteractResponse)
async def interact_with_station(data: InteractRequest, request: Request):
    game: GameState  = request.app.state.game
    async with game.lock: 
        ingredient = data.heldIngredient
        station = game.kitchen.get_furniture(data.stationId)

        if station != None:
            ingredient = station.held
            return InteractResponse(
                bSuccess=True,
                Message="Chef tomó un tomate.",
                Score=0,
                UpdatedHeldIngredient=ingredient,
                ActiveRecipes=[]
            )

    if request.stationId.startswith("cutting_board"):
        if ingredient.type == "Vegetal" and ingredient.state == "Crudo":
            ingredient.state = "Cortado"

            return InteractResponse(
                bSuccess=True,
                Message=f"{ingredient.Name} fue cortado.",
                Score=0,
                UpdatedHeldIngredient=ingredient,
                ActiveRecipes=[]
            )

        return InteractResponse(
            bSuccess=False,
            Message="Esta estación solo puede cortar vegetales crudos.",
            Score=0,
            UpdatedHeldIngredient=ingredient,
            ActiveRecipes=[]
        )

    return InteractResponse(
        bSuccess=False,
        Message="La estación no tiene una acción válida.",
        Score=0,
        UpdatedHeldIngredient=ingredient,
        ActiveRecipes=[]
    )