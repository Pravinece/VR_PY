
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.userModel import GameEnum, StagesModel


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
            doc["id"] = str(doc["_id"])
            stages.append(doc)
        return stages

    async def get_stage_by_id(self, stage_id: str) -> dict | None:
        try:
            object_id = ObjectId(stage_id)
        except Invalid:
            return None

        doc = await self.collection.find_one({"_id": object_id})
        if doc:
            doc["id"] = str(doc["_id"])
            return doc
        return None

    async def create_stage(self, stage_data):
        stage_dict = stage_data.model_dump()
        result = await self.collection.insert_one(stage_dict)
        
        stage_dict["id"] = str(result.inserted_id)
        return stage_dict


    def update_stage(self, stage_id, stage_data):
        return self.stageRepository.update_stage(stage_id, stage_data)

    def delete_stage(self, stage_id):
        return self.stageRepository.delete_stage(stage_id)