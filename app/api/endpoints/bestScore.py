from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.db import mongodb
from app.core.security import get_current_user, require_roles
from app.schema.bestScoreSchema import BestScoreLeaderboardRes, UpdateCleanDealBestScoreReq, UpdateSkateBestScoreReq
from app.schema.userSchema import APIResponse
from app.services.bestScoreService import BestScoreService

router = APIRouter()


async def get_db() -> AsyncIOMotorDatabase:
    return await mongodb.get_database()


@router.patch("/best-scores/skating", response_model=APIResponse)
async def update_skate_best_score(
    payload: UpdateSkateBestScoreReq,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = BestScoreService(db)
    await service.update_skate_best_score(payload.user_id, payload.session_id, payload.mode)
    return APIResponse(success=True, message="Best score updated successfully", data=None)


@router.patch("/best-scores/cleandeal", response_model=APIResponse)
async def update_cleandeal_best_score(
    payload: UpdateCleanDealBestScoreReq,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = BestScoreService(db)
    await service.update_cleandeal_best_score(payload.user_id, payload.session_id, payload.mode)
    return APIResponse(success=True, message="Best score updated successfully", data=None)


@router.get("/best-scores", response_model=APIResponse[BestScoreLeaderboardRes])
async def get_best_scores(
    game_type: str = Query(...),
    mode: str = Query(...),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = BestScoreService(db)
    result = await service.get_leaderboard(game_type, mode, page, limit, current_user["id"])
    return APIResponse(success=True, message="Best scores fetched successfully", data=result)


@router.get("/player-participant")
async def get_count(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(require_roles("superadmin")),
):
    service = BestScoreService(db)
    data = await service.get_user_count()
    
    return APIResponse(success=True, message="Count fetched successfully", data=data)
