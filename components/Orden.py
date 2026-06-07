from pydantic import BaseModel
from components.Recipe import Recipe

class Orden(BaseModel):
    recipe: Recipe = None
    status: bool = False