import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.client_session import ClientSession
from app.models.userModel import AvatarModel, GenderEnum
from app.schema.avatarSchema import AvatarRes, AvatarWithAssetsRes, EquippedAssetDetail
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

    async def equip_asset(self, user_id: str, asset_id: str) -> AvatarWithAssetsRes:
        try:
            asset = await self.assets_collection.find_one({"_id": asset_id})
            if not asset:
                raise AppException(status_code=404, message="Asset not found")

            avatar = await self.collection.find_one({"user_id": user_id, "gender": asset["gender"]})
            if not avatar:
                raise AppException(status_code=404, message="Avatar not found for this user and gender")

            equipped = avatar.get("equipped_assets", [])

            if asset_id in equipped:
                raise AppException(status_code=409, message="Asset is already equipped")

            # check asset is default or unlocked by user
            if not asset["is_default"]:
                unlocked = await self.collection.database["unlocked_assets"].find_one(
                    {"user_id": user_id, "asset_id": asset_id}
                )
                if not unlocked:
                    raise AppException(status_code=403, message="Asset is not unlocked by this user")

            # find existing asset of same type and remove it
            same_type_assets = await self.assets_collection.find(
                {"_id": {"$in": equipped}, "type": asset["type"]}
            ).to_list(length=None)
            ids_to_remove = [a["_id"] for a in same_type_assets]

            updated_equipped = [aid for aid in equipped if aid not in ids_to_remove]
            updated_equipped.append(asset_id)

            await self.collection.update_one(
                {"_id": avatar["_id"]},
                {"$set": {"equipped_assets": updated_equipped}},
            )

            asset_docs = await self.assets_collection.find({"_id": {"$in": updated_equipped}}).to_list(length=None)
            asset_map = {a["_id"]: a for a in asset_docs}

            return AvatarWithAssetsRes(
                id=str(avatar["_id"]),
                gender=avatar["gender"],
                equipped_assets=[
                    EquippedAssetDetail(
                        id=str(aid),
                        name=asset_map[aid]["name"],
                        gender=asset_map[aid]["gender"],
                        type=asset_map[aid]["type"],
                        image=asset_map[aid]["image"],
                        is_default=asset_map[aid]["is_default"],
                    )
                    for aid in updated_equipped if aid in asset_map
                ],
            )
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in equip_asset")
            raise AppException(status_code=500, message="Failed to equip asset")
