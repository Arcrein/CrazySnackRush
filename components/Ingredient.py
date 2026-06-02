from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

class Ingredient(BaseModel):
    isCut: bool = False
    isTrash: bool = False
    isMixed: bool = False
    isFried: bool = False
    isDeepFried: bool = False
    isBoiled: bool = False
    canCut: bool = False
    canMix: bool = False
    canFry: bool = False
    canDeepFry: bool = False
    canBoil: bool = False
    name: str = ""
    