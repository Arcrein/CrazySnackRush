from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from components.Ingredient import Ingredient

class Furniture(BaseModel):
    stationId: int = 0
    type: str = "Table"
    held: BaseModel = None

class IngredientBox(Furniture):
    contains: Ingredient