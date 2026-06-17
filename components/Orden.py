from pydantic import BaseModel
from components.Recipe import Recipe

class Orden(BaseModel):
    id: int = 0
    recipe: Recipe = None
    status: bool = False
    time_remaining: float = 0.0
    start_time: float = 0.0