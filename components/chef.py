from pydantic import BaseModel

class chef(BaseModel):
    "name" = str = ""
    "points" = int = 0