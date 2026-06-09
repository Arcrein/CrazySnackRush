from pydantic import BaseModel

class  ObjectDto(BaseModel):
    name: str = ""
    state: str = ""
