from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.db import mongodb
from app.schema.cleanDealSchema import (
    CreateCleanDealSessionReq, UpdateCleanDealSessionReq,
    CleanDealSessionRes, PaginatedCleanDealSessionRes
)
from app.schema.userSchema import APIResponse
from app.services.cleanDealService import CleanDealService
from app.core.security import get_current_user, require_roles

router = APIRouter()


async def get_db() -> AsyncIOMotorDatabase:
    return await mongodb.get_database()


@router.get("/cleandeal/sessions", response_model=APIResponse[PaginatedCleanDealSessionRes])
async def get_all_cleandeal_sessions(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_db),
    mode: str = Query(default="easy", pattern="^(easy|medium|hard)$"),
    search: str = Query(default=None),
    current_user: dict = Depends(require_roles("superadmin")),
):
    service = CleanDealService(db)
    result = await service.get_sessions(page, limit, mode, search)
    return APIResponse(success=True, message="Clean deal sessions fetched successfully", data=result)

@router.get("/cleandeal/{session_id}", response_model=APIResponse[CleanDealSessionRes])
async def getPastSessions(
    session_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = CleanDealService(db)
    result = await service.get_session_by_id(session_id=session_id)
    return APIResponse(success=True, message="Sessions retrieved successfully", data=result)

@router.post("/cleandeal/sessions", response_model=APIResponse[CleanDealSessionRes])
async def create_session(
    payload: CreateCleanDealSessionReq,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = CleanDealService(db)
    result = await service.create_session(payload)
    return APIResponse(success=True, message="Session created successfully", data=result)


@router.patch("/cleandeal/sessions/{session_id}", response_model=APIResponse[CleanDealSessionRes])
async def update_session(
    session_id: str,
    payload: UpdateCleanDealSessionReq,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = CleanDealService(db)
    result = await service.update_session(session_id, payload)
    return APIResponse(success=True, message="Session updated successfully", data=result)
