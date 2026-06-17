from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
from components.Kitchen import kitchen
import components.Furniture as F 
import components.Ingredient as I
import asyncio
import time
from components.Recipe import load_recipes, load_ingredients

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
    stationId: str
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

@app.post("/game/interact", response_model=InteractResponse)
async def interact_with_station(data: InteractRequest, request: Request):
    game: GameState = request.app.state.game
    async with game.lock:
        ingredient = data.heldIngredient

        if data.stationId.startswith("pantry_tomato"):
            ingredient = IngredientDto(name="Tomate", type="Vegetal", state="Crudo")
            return InteractResponse(bSuccess=True, Message="Chef tomó un tomate.", Score=0, UpdatedHeldIngredient=ingredient, ActiveRecipes=[])

        if data.stationId.startswith("cutting_board"):
            ingredient_data = find_ingredient(ingredient.name)
            if ingredient_data and ingredient_data.canCut:
                ingredient.state = "Cortado"
                return InteractResponse(bSuccess=True, Message=f"{ingredient.name} fue cortado.", Score=0, UpdatedHeldIngredient=ingredient, ActiveRecipes=[])
            return InteractResponse(bSuccess=False, Message="Este ingrediente no se puede cortar.", Score=0, UpdatedHeldIngredient=ingredient, ActiveRecipes=[])

        if data.stationId.startswith("trash"):
            ingredient = IngredientDto()
            return InteractResponse(bSuccess=True, Message="Ingrediente desechado.", Score=0, UpdatedHeldIngredient=ingredient, ActiveRecipes=[])

        if data.stationId.startswith("burner"):
            ingredient_data = find_ingredient(ingredient.name)
            if ingredient_data and ingredient_data.canFry:
                ingredient.state = "Cooked"
                return InteractResponse(bSuccess=True, Message=f"{ingredient.name} fue cocinado.", Score=0, UpdatedHeldIngredient=ingredient, ActiveRecipes=[])
            return InteractResponse(bSuccess=False, Message="Este ingrediente no se puede cocinar.", Score=0, UpdatedHeldIngredient=ingredient, ActiveRecipes=[])

        if data.stationId.startswith("deepFryer"):
            ingredient_data = find_ingredient(ingredient.name)
            if ingredient_data and ingredient_data.canDeepFry:
                ingredient.state = "DeepFried"
                return InteractResponse(bSuccess=True, Message=f"{ingredient.name} fue freído.", Score=0, UpdatedHeldIngredient=ingredient, ActiveRecipes=[])
            return InteractResponse(bSuccess=False, Message="Este ingrediente no se puede freír.", Score=0, UpdatedHeldIngredient=ingredient, ActiveRecipes=[])

        if data.stationId.startswith("sink"):
            if ingredient.name == "Plate" and ingredient.state == "Dirty":
                ingredient.state = "Clean"
                return InteractResponse(bSuccess=True, Message="El plato fue limpiado.", Score=0, UpdatedHeldIngredient=ingredient, ActiveRecipes=[])
            return InteractResponse(bSuccess=False, Message="La pila solo acepta platos sucios.", Score=0, UpdatedHeldIngredient=ingredient, ActiveRecipes=[])

        if data.stationId.startswith("boiler"):
            ingredient_data = find_ingredient(ingredient.name)
            if ingredient_data and ingredient_data.canBoil:
                ingredient.state = "Boiled"
                return InteractResponse(bSuccess=True, Message=f"{ingredient.name} fue hervido.", Score=0, UpdatedHeldIngredient=ingredient, ActiveRecipes=[])
            return InteractResponse(bSuccess=False, Message="Este ingrediente no se puede hervir.", Score=0, UpdatedHeldIngredient=ingredient, ActiveRecipes=[])

        if data.stationId.startswith("servingStation"):
            if ingredient.type == "Recipe" and ingredient.state == "Ready":
                matching_order = next(
                    (o for o in game.kitchen.order_list if o.recipe.name == ingredient.name and o.recipe.canDeliver),
                    None
                )
                if matching_order:
                    game.kitchen.order_list.remove(matching_order)
                    game.kitchen.points += matching_order.recipe.currentPoints
                    return InteractResponse(bSuccess=True, Message=f"Orden de {ingredient.name} entregada!", Score=game.kitchen.points, UpdatedHeldIngredient=IngredientDto(), ActiveRecipes=[])
            return InteractResponse(bSuccess=False, Message="No hay ninguna orden activa para este platillo.", Score=0, UpdatedHeldIngredient=ingredient, ActiveRecipes=[])

        return InteractResponse(bSuccess=False, Message="La estación no tiene una acción válida.", Score=0, UpdatedHeldIngredient=ingredient, ActiveRecipes=[])