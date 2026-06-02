from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import Furniture as F 

class kitchen(BaseModel):
    name: str = ""
    type: str = ""
    state: str = ""
    furnitureList: List[F.Furniture] = []