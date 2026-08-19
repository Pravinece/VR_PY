from fastapi import APIRouter, Depends
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.db import mongodb
from app.schema.unlockedAssetSchema import UnlockAssetReq, UnlockedAssetRes
from app.schema.userSchema import APIResponse
from app.services.unlockedAssetService import UnlockedAssetService
from app.core.security import get_current_user

router = APIRouter()


async def get_db() -> AsyncIOMotorDatabase:
    return await mongodb.get_database()


@router.get("/users/{user_id}/unlocked-assets", response_model=APIResponse[List[UnlockedAssetRes]])
async def get_unlocked_assets(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = UnlockedAssetService(db)
    result = await service.get_unlocked_assets(user_id)
    return APIResponse(success=True, message="Unlocked assets fetched successfully", data=result)


@router.post("/users/{user_id}/unlocked-assets", response_model=APIResponse[UnlockedAssetRes])
async def unlock_asset(
    user_id: str,
    payload: UnlockAssetReq,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = UnlockedAssetService(db)
    result = await service.unlock_asset(user_id, payload)
    return APIResponse(success=True, message="Asset unlocked successfully", data=result)


@router.delete("/users/{user_id}/unlocked-assets/{asset_id}", response_model=APIResponse)
async def delete_unlocked_asset(
    user_id: str,
    asset_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = UnlockedAssetService(db)
    await service.delete_unlocked_asset(user_id, asset_id)
    return APIResponse(success=True, message="Unlocked asset removed successfully")
