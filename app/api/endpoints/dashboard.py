from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.db import mongodb
from app.core.security import require_roles
from app.schema.dashboardSchema import GameStatsRes
from app.schema.userSchema import APIResponse
from app.services.dashboardService import DashboardService

router = APIRouter()


async def get_db() -> AsyncIOMotorDatabase:
    return await mongodb.get_database()


@router.get("/dashboard/game-stats", response_model=APIResponse[GameStatsRes])
async def get_game_stats(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(require_roles("superadmin")),
):
    service = DashboardService(db)
    stats = await service.get_monthly_game_stats()
    return APIResponse(success=True, message="Game stats fetched successfully", data=stats)
