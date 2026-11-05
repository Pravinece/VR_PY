import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.userModel import GameEnum
from app.schema.stageSchema import StagesModel, createStageReq

logger = logging.getLogger(__name__)

class stageService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["stages"]
        self.db = db

    async def get_stages(self, game: GameEnum | None = None) -> list[dict]:
        query = {}
        if game:
            query["game"] = game.value

        cursor = self.collection.find(query)
        stages = []
        async for doc in cursor:
            doc["id"] = doc["_id"] 
            stages.append(doc)
        return stages

    async def get_stage_by_id(self, stage_id: str) -> dict | None:
        doc = await self.collection.find_one({"_id": stage_id})
        if doc:
            doc["id"] = doc["_id"]
            return doc
        return None

    async def create_stage(self, stage_data: createStageReq) -> dict:
        stage_model = StagesModel(**stage_data.model_dump())
        stage_dict = stage_model.model_dump(by_alias=True)
        
        await self.collection.insert_one(stage_dict)
        
        stage_dict["id"] = stage_dict["_id"]
        return stage_dict