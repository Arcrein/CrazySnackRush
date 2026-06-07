from pydantic import BaseModel
from typing import List
from components.Ingredient import Ingredient

class Furniture(BaseModel):
    stationId: int = 0
    type: str = "Table"
    held: BaseModel = None

class IngredientBox(Furniture):
    contains: Ingredient 

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

