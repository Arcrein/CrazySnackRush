from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from components.core import IngredientDto, ObjectDto
from components.Ingredient import Ingredient
from components.Orden import Orden
from components.Recipe import Recipe, find_matching_recipes


CUTTINGTIME: float = 2.0
COOKINGTIME: float = 12.0
BURNTIME: float = COOKINGTIME * 2.0

SINGLE_SLOT_CONTAINERS = {"Pot", "FryPan", "FryBasket"}
MULTI_SLOT_CONTAINERS = {"Plate", "Mug"}
ALL_CONTAINERS = SINGLE_SLOT_CONTAINERS | MULTI_SLOT_CONTAINERS
HEATED_CONTAINERS = {"Pot", "FryPan", "FryBasket"}


def getIngredient(ingredientList: List[Ingredient], name: str):
    for ing in ingredientList:
        if ing.name == name:
            return ing
    return None


def getTransformationResult(ingredient: Ingredient, work_type: str) -> str:
    if work_type == "Cut":
        return ingredient.cutResult
    if work_type == "Mix":
        return ingredient.mixResult
    if work_type == "Fry":
        return ingredient.fryResult
    if work_type == "DeepFry":
        return ingredient.deepFryResult
    if work_type == "Boil":
        return ingredient.boilResult
    if work_type == "Burn":
        return ingredient.burnResult
    return ""


def transformObject(obj: ObjectDto | IngredientDto, ingredientList: List[Ingredient], work_type: str) -> bool:
    ingredient = getIngredient(ingredientList, obj.name)
    if ingredient is None:
        return False

    result_name = getTransformationResult(ingredient, work_type)
    if result_name == "":
        return False

    result_ingredient = getIngredient(ingredientList, result_name)
    if result_ingredient is None:
        return False

    obj.name = result_ingredient.name
    obj.state = result_ingredient.state
    return True


def isContainer(obj: ObjectDto) -> bool:
    return obj.name in ALL_CONTAINERS


def containerCapacity(container: ObjectDto) -> int:
    if container.name in SINGLE_SLOT_CONTAINERS:
        return 1
    if container.name in MULTI_SLOT_CONTAINERS:
        return 10
    return 0


def canAddToContainer(
    container: ObjectDto,
    obj: ObjectDto,
    ingredientList: List[Ingredient],
    recipeList: Optional[List[Recipe]] = None
) -> tuple[bool, List[Recipe]]:
    if not isContainer(container):
        return False, []
    if obj.name == "":
        return False, []
    if isContainer(obj):
        return False, []
    if len(container.held) >= containerCapacity(container):
        return False, []

    ingredient = getIngredient(ingredientList, obj.name)
    if container.name == "Plate":
        if ingredient is None or not ingredient.isReady:
            return False, []

        candidate_items = list(container.held)
        candidate_items.append(IngredientDto(name=obj.name, state=obj.state))

        if recipeList is None:
            return False, []
        
        matchingRecipes = find_matching_recipes(candidate_items, recipeList, deliverable_only=True)
        return len(matchingRecipes) > 0, matchingRecipes

    if container.name == "Mug":
        return True, []

    if ingredient is None:
        return False, []

    if container.name == "Pot":
        return ingredient.canBoil, []
    if container.name == "FryPan":
        return ingredient.canFry, []
    if container.name in {"FryBasket"}:
        return ingredient.canDeepFry, []

    return False, []


def addToContainer(
    container: ObjectDto,
    obj: ObjectDto,
    ingredientList: List[Ingredient],
    recipeList: Optional[List[Recipe]] = None
) -> tuple[bool, List[Recipe]]:
    can_add, matching_recipes = canAddToContainer(container, obj, ingredientList, recipeList)
    if not can_add:
        return False, matching_recipes
    container.held.append(IngredientDto(name=obj.name, state=obj.state))
    return True, matching_recipes

def resetContainerWork(container: ObjectDto):
    container.progress = 0.0
    container.isActive = False
    container.workType = ""
    container.lastStartTime = 0.0


def getContainerWorkType(container: ObjectDto) -> str:
    if container.name == "Pot":
        return "Boil"
    if container.name == "FryPan":
        return "Fry"
    if container.name in {"FryBasket"}:
        return "DeepFry"
    return ""


def finishContainerWorkIfReady(container: ObjectDto, ingredientList: List[Ingredient]) -> bool:
    if len(container.held) == 0:
        return False

    ingredient_obj = container.held[0]
    ingredient = getIngredient(ingredientList, ingredient_obj.name)

    if ingredient is not None and ingredient.canBurn and container.progress >= 2:
        return transformObject(ingredient_obj, ingredientList, "Burn")

    work_type = getContainerWorkType(container)
    if work_type != "" and container.progress >= 1 and ingredient.isBurned == False:
        transformObject(ingredient_obj, ingredientList, work_type)

    return False


def syncContainerWork(container: ObjectDto, ingredientList: List[Ingredient], pause_work: bool) -> bool:
    if container.isActive:
        now_ts = datetime.now().timestamp()
        container.progress += (now_ts - container.lastStartTime) / COOKINGTIME

        if pause_work:
            container.isActive = False
            container.lastStartTime = 0.0
        else:
            container.lastStartTime = now_ts

    burned = finishContainerWorkIfReady(container, ingredientList)

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

    if container.name == "Pot":
        if not ingredient.canBoil or ingredient.boilResult == "":
            return False
        container.workType = "Boil"
    elif container.name == "FryPan":
        if not ingredient.canFry or ingredient.fryResult == "":
            return False
        container.workType = "Fry"
    elif container.name in {"FryBasket"}:
        if not ingredient.canDeepFry or ingredient.deepFryResult == "":
            return False
        container.workType = "DeepFry"

    container.isActive = True
    container.lastStartTime = datetime.now().timestamp()
    return True


def recipeMatchesPlateExactly(recipe: Recipe, plate_ingredients: List[IngredientDto]) -> bool:
    if len(plate_ingredients) != len(recipe.requiredIngredients):
        return False

    return recipe.recipeMatchesIngredients(plate_ingredients)


def findPendingOrderForPlate(plate: ObjectDto, orderList: Optional[List[Orden]]) -> Optional[Orden]:
    if plate.name != "Plate":
        return None
    if len(plate.held) == 0:
        return None
    if orderList is None:
        return None

    best_order: Optional[Orden] = None

    for order in orderList:
        if order.status:
            continue
        if order.recipe is None:
            continue
        if not recipeMatchesPlateExactly(order.recipe, plate.held):
            continue

        if best_order is None or order.time_remaining < best_order.time_remaining:
            best_order = order

    return best_order


def buildCompletedOrderRecipe(order: Orden) -> Recipe:
    recipe = order.recipe.model_copy(deep=True)
    recipe.orderId = order.id
    recipe.timeRemaining = order.time_remaining
    return recipe


def failResponse(
    held: ObjectDto,
    message: str = "No funca.",
    score: int = 0,
    is_in_fire: bool = False,
    matching_recipes: Optional[List[Recipe]] = None
) -> "InteractResponse":
    return InteractResponse(
        bSuccess=False,
        Message=message,
        Score=score,
        UpdatedHeld=held,
        ActiveRecipes=matching_recipes if matching_recipes is not None else [],
        isInFire=is_in_fire
    )


def clearHandResponse(
    message: str = "transfer",
    score: int = 0,
    is_in_fire: bool = False,
    matching_recipes: Optional[List[Recipe]] = None
) -> "InteractResponse":
    return InteractResponse(
        bSuccess=True,
        Message=message,
        Score=score,
        UpdatedHeld=ObjectDto(),
        ActiveRecipes=matching_recipes if matching_recipes is not None else [],
        isInFire=is_in_fire
    )


def transferObjectResponse(
    obj: ObjectDto,
    message: str = "transfer",
    score: int = 0,
    is_in_fire: bool = False,
    matching_recipes: Optional[List[Recipe]] = None
) -> "InteractResponse":
    return InteractResponse(
        bSuccess=True,
        Message=message,
        Score=score,
        UpdatedHeld=obj,
        ActiveRecipes=matching_recipes if matching_recipes is not None else [],
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
    ActiveRecipes: List[Recipe] = Field(default_factory=list)
    isInFire: bool = False


class Furniture(BaseModel):
    stationId: int = 0
    type: str = "Table"
    held: ObjectDto = Field(default_factory=ObjectDto)
    isInFire: bool = False

    def doInteract(
        self,
        request: InteractRequest,
        ingredientList: List[Ingredient],
        recipeList: Optional[List[Recipe]] = None,
        orderList: Optional[List[Orden]] = None
    ) -> InteractResponse:
        return failResponse(request.held)

    def sync(self, ingredientList: List[Ingredient]) -> bool:
        if self.held.name in HEATED_CONTAINERS:
            if syncContainerWork(self.held, ingredientList, pause_work=False):
                self.isInFire = True


class IngredientBox(Furniture):
    contains: Ingredient

    def doInteract(
        self,
        request: InteractRequest,
        ingredientList: List[Ingredient],
        recipeList: Optional[List[Recipe]] = None,
        orderList: Optional[List[Orden]] = None
    ) -> InteractResponse:
        if self.held.name == "" and request.held.name == "":
            ingredient = ObjectDto(name=self.contains.name, state=self.contains.state)
            return transferObjectResponse(ingredient)

        if self.held.name != "" and request.held.name == "":
            obj = self.held
            self.held = ObjectDto()
            return transferObjectResponse(obj)

        if self.held.name == "" and request.held.name != "":
            self.held = request.held
            return clearHandResponse()

        if self.held.name != "" and request.held.name != "":
            could_add, matching_recipes = addToContainer(self.held, request.held, ingredientList, recipeList)
            if could_add:
                return clearHandResponse(matching_recipes=matching_recipes)

            return failResponse(request.held, "Nadie tomo nada.")

        return failResponse(request.held)


class stove(Furniture):
    def doInteract(
        self,
        request: InteractRequest,
        ingredientList: List[Ingredient],
        recipeList: Optional[List[Recipe]] = None,
        orderList: Optional[List[Orden]] = None
    ) -> InteractResponse:
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
            could_add, matching_recipes = addToContainer(self.held, request.held, ingredientList, recipeList)
            if could_add:
                if self.held.name in HEATED_CONTAINERS:
                    resetContainerWork(self.held)
                    startContainerWork(self.held, ingredientList)
                return clearHandResponse(is_in_fire=self.isInFire, matching_recipes=matching_recipes)

            return failResponse(request.held, is_in_fire=self.isInFire, matching_recipes=matching_recipes)

        return failResponse(request.held, is_in_fire=self.isInFire)


class cuttingBoard(Furniture):
    isCutting: bool = False
    cuttingStartTime: datetime = Field(default_factory=datetime.now)
    cuttingDeltaTime: float = 0.0

    def doInteract(
        self,
        request: InteractRequest,
        ingredientList: List[Ingredient],
        recipeList: Optional[List[Recipe]] = None,
        orderList: Optional[List[Orden]] = None
    ) -> InteractResponse:
        if self.held.name != "" and request.held.name != "":
            could_add, matching_recipes = addToContainer(self.held, request.held, ingredientList, recipeList)
            if could_add:
                return clearHandResponse(matching_recipes=matching_recipes)

            return failResponse(request.held, matching_recipes=matching_recipes)

        if self.held.name == "" and request.held.name != "" and request.action == "interact":
            self.held = request.held
            self.isCutting = False
            self.cuttingDeltaTime = 0.0
            return clearHandResponse()

        if self.held.name != "" and request.held.name == "" and request.action == "activate":
            ingredient = getIngredient(ingredientList, self.held.name)

            if ingredient is not None and ingredient.canCut and ingredient.cutResult != "":
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
                    transformObject(self.held, ingredientList, "Cut")

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
    def doInteract(
        self,
        request: InteractRequest,
        ingredientList: List[Ingredient],
        recipeList: Optional[List[Recipe]] = None,
        orderList: Optional[List[Orden]] = None
    ) -> InteractResponse:
        if request.action != "interact":
            return failResponse(request.held)

        if not isContainer(request.held):
            return failResponse(request.held)

        return clearHandResponse(message="clear")


class servingStation(Furniture):
    def doInteract(
        self,
        request: InteractRequest,
        ingredientList: List[Ingredient],
        recipeList: Optional[List[Recipe]] = None,
        orderList: Optional[List[Orden]] = None
    ) -> InteractResponse:
        if request.action != "interact":
            return failResponse(request.held)

        if request.held.name != "Plate":
            return failResponse(request.held)

        if len(request.held.held) == 0:
            return failResponse(request.held)

        matched_order = findPendingOrderForPlate(request.held, orderList)
        if matched_order is None or matched_order.recipe is None:
            return failResponse(request.held, "No hay una orden pendiente para ese plato.")

        completed_recipe = buildCompletedOrderRecipe(matched_order)
        return clearHandResponse(matching_recipes=[completed_recipe])


class table(Furniture):
    def doInteract(
        self,
        request: InteractRequest,
        ingredientList: List[Ingredient],
        recipeList: Optional[List[Recipe]] = None,
        orderList: Optional[List[Orden]] = None
    ) -> InteractResponse:
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
            could_add, matching_recipes = addToContainer(self.held, request.held, ingredientList, recipeList)
            if could_add:
                return clearHandResponse(matching_recipes=matching_recipes)

            return failResponse(request.held, matching_recipes=matching_recipes)

        return failResponse(request.held)


class sink(Furniture):
    pass


class dish_spawner(Furniture):
    pass
