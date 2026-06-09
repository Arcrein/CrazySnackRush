from pydantic import BaseModel
from typing import List
from components.core import ObjectDto
from components.Ingredient import Ingredient, IngredientDto
from components.Recipe import RecipeDto
from components.Kitchen import kitchen
from datetime import datetime, timedelta


CUTTINGTIME = 2.0
COOKINGTIME = 12.0

class InteractRequest(BaseModel):
    chefId: int = -1
    stationId: int = -1
    action: str = ""
    held: ObjectDto = ObjectDto()


class InteractResponse(BaseModel):
    bSuccess: bool = False
    Message: str = ""
    Score: int = 0
    UpdatedHeld: ObjectDto = ObjectDto()
    ActiveRecipes: List[RecipeDto] = []

class Furniture(BaseModel):
    stationId: int = 0
    type: str = "Table"
    held: ObjectDto = ObjectDto()

    def doInteract(self, request: InteractRequest, kitchen: kitchen) -> InteractResponse:
        pass

class IngredientBox(Furniture):
    contains: Ingredient 

    def doInteract(self, request: InteractRequest, kitchen: kitchen) -> InteractResponse:
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
    isCutting: bool = False
    cuttingStartTime: datetime
    cuttingDeltaTime: float = 0

    def doInteract(self, request: InteractRequest, kitchen: kitchen) -> InteractResponse:
        if self.held.name != "" and request.held.name != "":
            return InteractResponse(
                bSuccess=False,
                Message="No funca.",
                Score=0,
                UpdatedHeld=request.held,
                ActiveRecipes=[]
                )
        elif self.held.name == "" and request.held.name != "" and request.action == "interact":
            self.held = request.held
            self.isCutting = False
            self.cuttingDeltaTime = 0
            return InteractResponse(
                bSuccess=True,
                Message="Si funca.",
                Score=0,
                UpdatedHeld=ObjectDto(),
                ActiveRecipes=[]
                )
        elif self.held.name != "" and request.held.name == "" and request.action == "activate":
            ingrediente = kitchen.getIngredient(self.held.name)
            if ingrediente != None and ingrediente.canCut:
                self.isCutting = True
                self.cuttingStartTime = datetime.now()

                return InteractResponse(
                    bSuccess= True,
                    Message="Casi",
                    Score=0,
                    UpdatedHeld=ObjectDto(),
                    ActiveRecipes=[]
                )
            else:
                return InteractResponse(
                bSuccess=False,
                Message="No funca.",
                Score=0,
                UpdatedHeld=request.held,
                ActiveRecipes=[]
                )
        elif self.held.name != "" and request.held.name == "" and request.action == "deactivate":
            if self.isCutting == True:
                self.isCutting = False
                self.cuttingDeltaTime += (datetime.now() - self.cuttingStartTime).total_seconds()
                return InteractResponse(
                    bSuccess= True,
                    Message="Casi",
                    Score=0,
                    UpdatedHeld=ObjectDto(),
                    ActiveRecipes=[]
                )
            else:
                return InteractResponse(
                bSuccess=False,
                Message="No funca.",
                Score=0,
                UpdatedHeld=request.held,
                ActiveRecipes=[]
                )
        elif self.held.name != "" and request.held.name == "" and request.action == "interact":
            if self.isCutting == True:
                return InteractResponse(
                    bSuccess=False,
                    Message="No funca.",
                    Score=0,
                    UpdatedHeld=request.held,
                    ActiveRecipes=[]
                )
            elif self.cuttingDeltaTime >= CUTTINGTIME:
                newIngredient = ObjectDto(name = self.held.name, state = "Cut")
                self.held = ObjectDto()
                return InteractResponse(
                    bSuccess=True,
                    Message="Funco.",
                    Score=0,
                    UpdatedHeld=newIngredient,
                    ActiveRecipes=[]
                )
        return InteractResponse(
                bSuccess=False,
                Message="No funca.",
                Score=0,
                UpdatedHeld=request.held,
                ActiveRecipes=[]
                )


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

