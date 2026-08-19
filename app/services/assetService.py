import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schema.assetSchema import CreateAssetReq, UpdateAssetReq, AssetRes, AssetListRes
from app.models.userModel import AssetModel
from app.core.exception import AppException

logger = logging.getLogger(__name__)


class AssetService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["assets"]

    async def create_asset(self, payload: CreateAssetReq) -> AssetRes:
        try:
            existing = await self.collection.find_one({"type": payload.type.value, "gender": payload.gender.value, "is_default": True})
            if existing:
                if payload.is_default and existing["is_default"]:
                    raise AppException(status_code=409, message=f"A default asset for type already exists")

            asset = AssetModel(
                name=payload.name,
                gender=payload.gender,
                type=payload.type,
                image=payload.image,
                is_default=payload.is_default,
                created_at=datetime.now(timezone.utc),
            )
            await self.collection.insert_one(asset.model_dump(by_alias=True))
            return AssetRes(
                id=asset.id,
                name=asset.name,
                gender=asset.gender,
                type=asset.type,
                image=asset.image,
                is_default=asset.is_default,
                created_at=asset.created_at,
            )
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in create_asset")
            raise AppException(status_code=500, message="Failed to create asset")

    async def update_asset(self, asset_id: str, payload: UpdateAssetReq) -> AssetRes:
        try:
            updates = {k: v for k, v in payload.model_dump().items() if v is not None}
            if not updates:
                raise AppException(status_code=400, message="No fields to update")

            result = await self.collection.find_one_and_update(
                {"_id": asset_id},
                {"$set": updates},
                return_document=True,
            )
            if not result:
                raise AppException(status_code=404, message="Asset not found")

            return AssetRes(
                id=result["_id"],
                name=result["name"],
                gender=result["gender"],
                type=result["type"],
                image=result["image"],
                is_default=result["is_default"],
                created_at=result["created_at"],
            )
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in update_asset")
            raise AppException(status_code=500, message="Failed to update asset")

    async def get_asset_by_id(self, asset_id: str) -> dict:
        asset = await self.collection.find_one({"_id": asset_id})
        if not asset:
            raise AppException(status_code=404, message="Asset not found")
        return asset

    async def get_default_assets(self, session=None) -> list:
        try:
            return await self.collection.find({"is_default": True}, session=session).to_list(length=None)
        except Exception:
            logger.exception("Unexpected error in get_default_assets")
            raise AppException(status_code=500, message="Failed to fetch default assets")

    async def get_assets(self) -> AssetListRes:
        try:
            data = await self.collection.find().to_list(length=None)
            assets = [
                AssetRes(
                    id=item["_id"],
                    name=item["name"],
                    gender=item["gender"],
                    type=item["type"],
                    image=item["image"],
                    is_default=item["is_default"],
                    created_at=item["created_at"],
                )
                for item in data
            ]
            return AssetListRes(assets=assets)
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in get_assets")
            raise AppException(status_code=500, message="Failed to fetch assets")
