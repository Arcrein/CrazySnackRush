from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from components.core import IngredientDto, ObjectDto
from components.Ingredient import Ingredient
from components.Recipe import RecipeDto


CUTTINGTIME: float = 2.0
COOKINGTIME: float = 12.0
BURNTIME: float = COOKINGTIME * 2.0

SINGLE_SLOT_CONTAINERS = {"Pot", "FryPan", "FryBasket", "FryBasquet"}
MULTI_SLOT_CONTAINERS = {"Plate", "Mug"}
ALL_CONTAINERS = SINGLE_SLOT_CONTAINERS | MULTI_SLOT_CONTAINERS
HEATED_CONTAINERS = {"Pot", "FryPan", "FryBasket", "FryBasquet"}


def getIngredient(ingredientList: List[Ingredient], name: str):
    for ing in ingredientList:
        if ing.name == name:
            return ing
    return None


def isContainer(obj: ObjectDto) -> bool:
    return obj.name in ALL_CONTAINERS


def containerCapacity(container: ObjectDto) -> int:
    if container.name in SINGLE_SLOT_CONTAINERS:
        return 1
    if container.name in MULTI_SLOT_CONTAINERS:
        return 10
    return 0


def canAddToContainer(container: ObjectDto, obj: ObjectDto, ingredientList: List[Ingredient]) -> bool:
    if not isContainer(container):
        return False
    if obj.name == "":
        return False
    if isContainer(obj):
        return False
    if len(container.held) >= containerCapacity(container):
        return False

    if container.name in MULTI_SLOT_CONTAINERS:
        return True

    ingredient = getIngredient(ingredientList, obj.name)
    if ingredient is None:
        return False

    if container.name == "Pot":
        return ingredient.canBoil
    if container.name == "FryPan":
        return ingredient.canFry
    if container.name in {"FryBasket", "FryBasquet"}:
        return ingredient.canDeepFry

    return False


def addToContainer(container: ObjectDto, obj: ObjectDto, ingredientList: List[Ingredient]) -> bool:
    if not canAddToContainer(container, obj, ingredientList):
        return False
    container.held.append(IngredientDto(name=obj.name, state=obj.state))
    return True


def resetContainerWork(container: ObjectDto):
    container.progress = 0.0
    container.isActive = False
    container.workType = ""
    container.lastStartTime = 0.0


def getCookedState(container: ObjectDto) -> str:
    if container.name == "Pot":
        return "Boiled"
    if container.name == "FryPan":
        return "Fried"
    if container.name in {"FryBasket", "FryBasquet"}:
        return "DeepFried"
    return ""


def finishContainerWorkIfReady(container: ObjectDto, ingredientList: List[Ingredient]) -> bool:
    if len(container.held) == 0:
        return False

    ingredient_obj = container.held[0]
    ingredient = getIngredient(ingredientList, ingredient_obj.name)

    if ingredient is not None and ingredient.canBurn and container.progress >= BURNTIME:
        ingredient_obj.state = "Burned"
        return True

    cooked_state = getCookedState(container)
    if cooked_state != "" and container.progress >= COOKINGTIME:
        ingredient_obj.state = cooked_state

    return False


def syncContainerWork(container: ObjectDto, ingredientList: List[Ingredient], pause_work: bool) -> bool:
    if container.isActive:
        now_ts = datetime.now().timestamp()
        container.progress += now_ts - container.lastStartTime

        if pause_work:
            container.isActive = False
            container.lastStartTime = 0.0
        else:
            container.lastStartTime = now_ts

    burned = finishContainerWorkIfReady(container, ingredientList)
    if burned:
        container.isActive = False
        container.lastStartTime = 0.0

    return burned


def pauseContainerWork(container: ObjectDto, ingredientList: List[Ingredient]) -> bool:
    return syncContainerWork(container, ingredientList, pause_work=True)


def startContainerWork(container: ObjectDto, ingredientList: List[Ingredient]) -> bool:
    if container.name not in HEATED_CONTAINERS:
        return False
    if len(container.held) == 0:
        return False

    ingredient_obj = container.held[0]
    ingredient = getIngredient(ingredientList, ingredient_obj.name)

    if ingredient is None:
        return False
    if ingredient_obj.state == "Burned":
        return False
    if container.progress >= BURNTIME:
        return False

    if container.name == "Pot":
        if not ingredient.canBoil:
            return False
        container.workType = "Boil"
    elif container.name == "FryPan":
        if not ingredient.canFry:
            return False
        container.workType = "Fry"
    elif container.name in {"FryBasket", "FryBasquet"}:
        if not ingredient.canDeepFry:
            return False
        container.workType = "DeepFry"

    container.isActive = True
    container.lastStartTime = datetime.now().timestamp()
    return True


def failResponse(
    held: ObjectDto,
    message: str = "No funca.",
    score: int = 0,
    is_in_fire: bool = False
) -> "InteractResponse":
    return InteractResponse(
        bSuccess=False,
        Message=message,
        Score=score,
        UpdatedHeld=held,
        ActiveRecipes=[],
        isInFire=is_in_fire
    )


def clearHandResponse(
    message: str = "transfer",
    score: int = 0,
    is_in_fire: bool = False
) -> "InteractResponse":
    return InteractResponse(
        bSuccess=True,
        Message=message,
        Score=score,
        UpdatedHeld=ObjectDto(),
        ActiveRecipes=[],
        isInFire=is_in_fire
    )


def transferObjectResponse(
    obj: ObjectDto,
    message: str = "transfer",
    score: int = 0,
    is_in_fire: bool = False
) -> "InteractResponse":
    return InteractResponse(
        bSuccess=True,
        Message=message,
        Score=score,
        UpdatedHeld=obj,
        ActiveRecipes=[],
        isInFire=is_in_fire
    )


class InteractRequest(BaseModel):
    chefId: int = -1
    stationId: int = -1
    action: str = ""
    held: ObjectDto = Field(default_factory=ObjectDto)


class InteractResponse(BaseModel):
    bSuccess: bool = False
    Message: str = ""
    Score: int = 0
    UpdatedHeld: ObjectDto = Field(default_factory=ObjectDto)
    ActiveRecipes: List[RecipeDto] = Field(default_factory=list)
    isInFire: bool = False


class Furniture(BaseModel):
    stationId: int = 0
    type: str = "Table"
    held: ObjectDto = Field(default_factory=ObjectDto)
    isInFire: bool = False

    def doInteract(self, request: InteractRequest, ingredientList: List[Ingredient]) -> InteractResponse:
        return failResponse(request.held)


class IngredientBox(Furniture):
    contains: Ingredient

    def doInteract(self, request: InteractRequest, ingredientList: List[Ingredient]) -> InteractResponse:
        if self.held.name == "" and request.held.name == "":
            ingredient = ObjectDto(name=self.contains.name)
            return transferObjectResponse(ingredient)

        if self.held.name != "" and request.held.name == "":
            obj = self.held
            self.held = ObjectDto()
            return transferObjectResponse(obj)

        if self.held.name == "" and request.held.name != "":
            self.held = request.held
            return clearHandResponse()

        if self.held.name != "" and request.held.name != "":
            if addToContainer(self.held, request.held, ingredientList):
                return clearHandResponse()

            return failResponse(request.held, "Nadie tomo nada.")

        return failResponse(request.held)


class stove(Furniture):
    def doInteract(self, request: InteractRequest, ingredientList: List[Ingredient]) -> InteractResponse:
        if request.action != "interact":
            return failResponse(request.held, is_in_fire=self.isInFire)

        if self.held.name in HEATED_CONTAINERS:
            if syncContainerWork(self.held, ingredientList, pause_work=False):
                self.isInFire = True

        if self.held.name == "" and request.held.name != "":
            self.held = request.held

            if self.held.name in HEATED_CONTAINERS:
                startContainerWork(self.held, ingredientList)

            return clearHandResponse(is_in_fire=self.isInFire)

        if self.held.name != "" and request.held.name == "":
            if self.held.name in HEATED_CONTAINERS:
                if pauseContainerWork(self.held, ingredientList):
                    self.isInFire = True

            obj = self.held
            self.held = ObjectDto()
            return transferObjectResponse(obj, is_in_fire=self.isInFire)

        if self.held.name != "" and request.held.name != "":
            if addToContainer(self.held, request.held, ingredientList):
                if self.held.name in HEATED_CONTAINERS:
                    resetContainerWork(self.held)
                    startContainerWork(self.held, ingredientList)
                return clearHandResponse(is_in_fire=self.isInFire)

            return failResponse(request.held, is_in_fire=self.isInFire)

        return failResponse(request.held, is_in_fire=self.isInFire)


class cuttingBoard(Furniture):
    isCutting: bool = False
    cuttingStartTime: datetime = Field(default_factory=datetime.now)
    cuttingDeltaTime: float = 0.0

    def doInteract(self, request: InteractRequest, ingredientList: List[Ingredient]) -> InteractResponse:
        if self.held.name != "" and request.held.name != "":
            if addToContainer(self.held, request.held, ingredientList):
                return clearHandResponse()

            return failResponse(request.held)

        if self.held.name == "" and request.held.name != "" and request.action == "interact":
            self.held = request.held
            self.isCutting = False
            self.cuttingDeltaTime = 0.0
            return clearHandResponse()

        if self.held.name != "" and request.held.name == "" and request.action == "activate":
            ingredient = getIngredient(ingredientList, self.held.name)

            if ingredient is not None and ingredient.canCut and self.held.state != "Cut":
                self.isCutting = True
                self.cuttingStartTime = datetime.now()
                return clearHandResponse("Casi")

            return failResponse(request.held)

        if self.held.name != "" and request.held.name == "" and request.action == "deactivate":
            if self.isCutting:
                self.isCutting = False
                self.cuttingDeltaTime += (datetime.now() - self.cuttingStartTime).total_seconds()
                percentage = int(self.cuttingDeltaTime / CUTTINGTIME * 100)

                if percentage >= 100:
                    self.held.state = "Cut"

                return transferObjectResponse(
                    self.held,
                    message=f"Progress: {percentage}",
                    score=min(100, percentage)
                )

            return failResponse(request.held)

        if self.held.name != "" and request.held.name == "" and request.action == "interact":
            if self.isCutting:
                return failResponse(request.held)

            if self.cuttingDeltaTime == 0 or self.cuttingDeltaTime >= CUTTINGTIME:
                obj = self.held
                self.held = ObjectDto()
                return transferObjectResponse(obj)

        return failResponse(request.held)


class mixer(Furniture):
    pass


class deepFryer(Furniture):
    pass


class trash(Furniture):
    pass


class servingStation(Furniture):
    pass


class table(Furniture):
    def doInteract(self, request: InteractRequest, ingredientList: List[Ingredient]) -> InteractResponse:
        if request.action != "interact":
            return failResponse(request.held)

        if self.held.name == "" and request.held.name != "":
            self.held = request.held
            return clearHandResponse()

        if self.held.name != "" and request.held.name == "":
            obj = self.held
            self.held = ObjectDto()
            return transferObjectResponse(obj)

        if self.held.name != "" and request.held.name != "":
            if addToContainer(self.held, request.held, ingredientList):
                return clearHandResponse()

            return failResponse(request.held)

        return failResponse(request.held)


class sink(Furniture):
    pass


class dish_spawner(Furniture):
    pass
