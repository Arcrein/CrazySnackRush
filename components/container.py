from components.Ingredient import Ingredient
from pydantic import BaseModel

class container(BaseModel):
    type: str = ""
    content: list = []
    cookPercentage: int = 0
    isINFIRE: bool = False
    
    def isEmpty(self):
        if len(self.content) == 0:
            return True

        else:
            return False

    def clear(self):
        self.content = []

    def addIngredient(self, ingredient: Ingredient):
        if self.type == "plate":
            self.content.append(ingredient)
        else:
            if  len(self.content) == 0:
                self.content.append(ingredient)
            
            else:
                print (self.type," esta lleno")
 
    def isInFire(self):
        isINFIRE = True