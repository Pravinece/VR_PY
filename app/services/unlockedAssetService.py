import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.userModel import UnlockedAssetModel
from app.schema.unlockedAssetSchema import UnlockAssetReq, UnlockedAssetRes
from app.core.exception import AppException
from app.services.userService import UserService
from app.services.assetService import AssetService

logger = logging.getLogger(__name__)


class UnlockedAssetService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["unlocked_assets"]
        self.user_service = UserService(db)
        self.asset_service = AssetService(db)

    async def unlock_asset(self, user_id: str, payload: UnlockAssetReq) -> UnlockedAssetRes:
        try:
            await self.user_service.get_user_by_id(user_id)
            await self.asset_service.get_asset_by_id(payload.asset_id)

            existing = await self.collection.find_one({"user_id": user_id, "asset_id": payload.asset_id})
            if existing:
                raise AppException(status_code=409, message="Asset already unlocked")

            unlocked = UnlockedAssetModel(
                user_id=user_id,
                asset_id=payload.asset_id,
                unlocked_at=datetime.now(timezone.utc),
            )
            await self.collection.insert_one(unlocked.model_dump(by_alias=True))
            return UnlockedAssetRes(
                id=unlocked.id,
                user_id=unlocked.user_id,
                asset_id=unlocked.asset_id,
                unlocked_at=unlocked.unlocked_at,
            )
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in unlock_asset")
            raise AppException(status_code=500, message="Failed to unlock asset")

    async def get_unlocked_assets(self, user_id: str) -> list[UnlockedAssetRes]:
        try:
            await self.user_service.get_user_by_id(user_id)
            data = await self.collection.find({"user_id": user_id}).to_list(length=None)
            return [
                UnlockedAssetRes(
                    id=item["_id"],
                    user_id=item["user_id"],
                    asset_id=item["asset_id"],
                    unlocked_at=item["unlocked_at"],
                )
                for item in data
            ]
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in get_unlocked_assets")
            raise AppException(status_code=500, message="Failed to fetch unlocked assets")

    async def delete_unlocked_asset(self, user_id: str, asset_id: str) -> None:
        try:
            result = await self.collection.delete_one({"user_id": user_id, "asset_id": asset_id})
            if result.deleted_count == 0:
                raise AppException(status_code=404, message="Unlocked asset not found")
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in delete_unlocked_asset")
            raise AppException(status_code=500, message="Failed to delete unlocked asset")
