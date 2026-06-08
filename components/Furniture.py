from pydantic import BaseModel
from typing import List
from components.core import ObjectDto
from components.Ingredient import Ingredient, IngredientDto
from components.Recipe import RecipeDto

class InteractRequest(BaseModel):
    chefId: int
    stationId: int
    action: str
    held: ObjectDto


class InteractResponse(BaseModel):
    bSuccess: bool
    Message: str
    Score: int
    UpdatedHeld: ObjectDto
    ActiveRecipes: List[RecipeDto]

class Furniture(BaseModel):
    stationId: int = 0
    type: str = "Table"
    held: ObjectDto

    def doInteract() -> InteractResponse:
        pass

class IngredientBox(Furniture):
    contains: Ingredient 

    def doInteract(self, request: InteractRequest) -> InteractResponse:
        if self.held.name == "" and request.held.name == "":
            ingredient = ObjectDto(name = self.contains.name)
            return InteractResponse(
                bSuccess=True,
                Message="Chef tomó un tomate.",
                Score=0,
                UpdatedHeld=ingredient,
                ActiveRecipes=[]
            )
        elif self.held.name != "" and request.held.name == "":
            ingredient = ObjectDto(name = self.held.name)
            self.held = None
            return InteractResponse(
                bSuccess=True,
                Message="Chef podria haber tomado un tomate.",
                Score=0,
                UpdatedHeld=ingredient,
                ActiveRecipes=[]
            )
        elif self.held.name == "" and request.held.name != "":
            self.held = request.held
            return InteractResponse(
                bSuccess=True,
                Message="Caja ha tomado un tomate.",
                Score=0,
                UpdatedHeld=ObjectDto(),
                ActiveRecipes=[]
            )
        elif self.held.name != "" and request.held.name != "":
            return InteractResponse(
                bSuccess=False,
                Message="Nadie tomo nada.",
                Score=0,
                UpdatedHeld=request.held,
                ActiveRecipes=[]
                )


class burner(Furniture):
    pass

class cuttingBoard(Furniture):
    pass

class mixer(Furniture):
    pass

class deepFryer(Furniture):
    pass

class trash(Furniture):
    pass

class servingStation(Furniture):
    pass

class table(Furniture):
    pass

class sink(Furniture):
    pass
    
class dish_spawner(Furniture):
    pass

