import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.db import MongoDB
from app.core.security import require_roles
from app.models.userModel import GameEnum
from app.schema.stageSchema import createStageReq, createStageRes, listStageRes
from app.schema.userSchema import APIResponse
from app.services import stageService

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_db() -> AsyncIOMotorDatabase:
    return await MongoDB.get_database()

@router.post("/stage", response_model=APIResponse[createStageRes])
async def post_stage(
    payload: createStageReq,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(require_roles("superadmin"))
):
    service = stageService(db)
    stage = await service.create_stage(payload)
    return APIResponse(success=True, message="Stage created successfully", data=stage)


@router.get("/stage", response_model=APIResponse[List[listStageRes]])
async def get_all_stages(
    game: GameEnum | None = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    service = stageService(db)
    stages = await service.get_stages(game=game)
    return APIResponse(success=True, message="Stages retrieved successfully", data=stages)


@router.get("/stage/{stage_id}", response_model=APIResponse[createStageRes])
async def get_stage_by_id(
    stage_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    service = stageService(db)
    stage = await service.get_stage_by_id(stage_id)
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Stage not found"
        )
    return APIResponse(success=True, message="Stage retrieved successfully", data=stage)