from components.Ingredient import Ingredient
from pydantic import BaseModel

class container(BaseModel):
    type: str = ""
    content: list = []
    cookPercentage: int = 0
    inFire: bool = False
    dirty: bool = False
    placed: bool = False
#===========================================================
#metodos
    def isEmpty(self):
        if len(self.content) == 0:
            return True

        else:
            return False
#___________________________________________________________
    def clear(self):
        self.content = []
#___________________________________________________________
    def addIngredient(self, ingredient: Ingredient):
        if self.type == "plate":
            self.content.append(ingredient)
        else:
            if  len(self.content) == 0:
                self.content.append(ingredient)
            
            else:
                print (self.type," esta lleno")
 #___________________________________________________________
    def isInFire(self):
        return self.inFire
#___________________________________________________________
    def isDirty(self):
        return self.dirty
#___________________________________________________________

    def isPlaced(self):
        return self.placed
    
#===========================================================

