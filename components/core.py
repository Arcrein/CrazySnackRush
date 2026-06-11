from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List

class IngredientDto(BaseModel):
    name: str = ""
    state: str = ""


class ObjectDto(BaseModel):
    name: str = ""
    state: str = ""
    held: List[IngredientDto] = Field(default_factory=list)

    progress: float = 0.0
    isActive: bool = False
    workType: str = ""
    lastStartTime: float = 0.0
