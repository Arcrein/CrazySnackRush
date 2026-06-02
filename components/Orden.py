from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

class Orden(BaseModel):
    name: str = ""
    type: str = ""
    state: str = ""