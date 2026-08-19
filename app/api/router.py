from fastapi import APIRouter
from app.api.endpoints.user import router as user_router
from app.api.endpoints.asset import router as asset_router
from app.api.endpoints.unlockedAsset import router as unlocked_asset_router

api_router = APIRouter()

api_router.include_router(user_router, tags=["Users"])
api_router.include_router(asset_router, tags=["Assets"])
api_router.include_router(unlocked_asset_router, tags=["Unlocked Assets"])
