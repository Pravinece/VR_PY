from fastapi import APIRouter
from app.api.endpoints.user import router as user_router
from app.api.endpoints.asset import router as asset_router
from app.api.endpoints.unlockedAsset import router as unlocked_asset_router
from app.api.endpoints.upload import router as upload_router
from app.api.endpoints.skateSession import router as skate_session_router
from app.api.endpoints.bestScore import router as best_score_router
from app.api.endpoints.cleanDeal import router as cleandeal_router
from app.api.endpoints.dashboard import router as dashboard_router

api_router = APIRouter()

api_router.include_router(user_router, tags=["Users"])
api_router.include_router(asset_router, tags=["Assets"])
api_router.include_router(unlocked_asset_router, tags=["Unlocked Assets"])
api_router.include_router(upload_router, tags=["Upload"])
api_router.include_router(skate_session_router, tags=["Skate Sessions"])
api_router.include_router(best_score_router, tags=["Best Scores"])
api_router.include_router(cleandeal_router, tags=["Clean Deal Sessions"])
api_router.include_router(dashboard_router, tags=["Dashboard"])
