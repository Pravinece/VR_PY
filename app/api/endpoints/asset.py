from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.db import mongodb
from app.schema.assetSchema import CreateAssetReq, UpdateAssetReq, AssetRes, AssetListRes
from app.schema.userSchema import APIResponse
from app.services.assetService import AssetService
from app.core.security import require_roles

router = APIRouter()


async def get_db() -> AsyncIOMotorDatabase:
    return await mongodb.get_database()


@router.post("/assets", response_model=APIResponse[AssetRes])
async def create_asset(
    payload: CreateAssetReq,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(require_roles("superadmin")),
):
    service = AssetService(db)
    asset = await service.create_asset(payload)
    return APIResponse(success=True, message="Asset created successfully", data=asset)


@router.put("/assets/{asset_id}", response_model=APIResponse[AssetRes])
async def update_asset(
    asset_id: str,
    payload: UpdateAssetReq,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(require_roles("superadmin")),
):
    service = AssetService(db)
    asset = await service.update_asset(asset_id, payload)
    return APIResponse(success=True, message="Asset updated successfully", data=asset)

@router.get("/assets", response_model=APIResponse[AssetListRes])
async def get_assets(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(require_roles("superadmin")),
):
    service = AssetService(db)
    assets = await service.get_assets()
    return APIResponse(success=True, message="Assets fetched successfully", data=assets)
