import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.client_session import ClientSession
from app.models.userModel import AvatarModel, GenderEnum
from app.schema.avatarSchema import AvatarRes
from app.core.exception import AppException

logger = logging.getLogger(__name__)


class AvatarService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["avatars"]
        self.assets_collection = db["assets"] 

    async def create_avatars_for_user(self, user_id: str, session: Optional[ClientSession] = None) -> list[AvatarRes]:
        try:
            existing = await self.collection.find_one({"user_id": user_id}, session=session)
            if existing:
                raise AppException(status_code=409, message="Avatars already exist for this user")

            # fetch default assets grouped by gender
            default_assets = await self.assets_collection.find({"is_default": True}, session=session).to_list(length=None)
            male_asset_ids = [a["_id"] for a in default_assets if a["gender"] == GenderEnum.MALE.value]
            female_asset_ids = [a["_id"] for a in default_assets if a["gender"] == GenderEnum.FEMALE.value]

            avatars = [
                AvatarModel(user_id=user_id, gender=GenderEnum.MALE, equipped_assets=male_asset_ids),
                AvatarModel(user_id=user_id, gender=GenderEnum.FEMALE, equipped_assets=female_asset_ids),
            ]
            await self.collection.insert_many([a.model_dump(by_alias=True) for a in avatars], session=session)
            return [
                AvatarRes(id=a.id, user_id=a.user_id, gender=a.gender, equipped_assets=a.equipped_assets)
                for a in avatars
            ]
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in create_avatars_for_user")
            raise AppException(status_code=500, message="Failed to create avatars")
