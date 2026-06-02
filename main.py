from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()


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


@app.post("/game/interact", response_model=InteractResponse)
def interact_with_station(request: InteractRequest):
    ingredient = request.heldIngredient

    if request.stationId.startswith("pantry_tomato"):
        ingredient = IngredientDto(
            name="Tomate",
            type="Vegetal",
            state="Crudo"
        )

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