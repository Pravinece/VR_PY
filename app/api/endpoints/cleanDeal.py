from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.db import mongodb
from app.core.security import get_current_user
from app.schema.cleanDealSchema import CreateCleanDealSessionReq, CleanDealSessionRes, PaginatedCleanDealSessionRes
from app.schema.userSchema import APIResponse
from app.services.cleanDealService import CleanDealService

router = APIRouter()


async def get_db() -> AsyncIOMotorDatabase:
    return await mongodb.get_database()


@router.post("/cleandeal-sessions", response_model=APIResponse[CleanDealSessionRes])
async def create_cleandeal_session(
    payload: CreateCleanDealSessionReq,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = CleanDealService(db)
    session = await service.create_session(payload)
    return APIResponse(success=True, message="Clean deal session created successfully", data=session)


@router.get("/cleandeal-sessions/session/{session_id}", response_model=APIResponse[CleanDealSessionRes])
async def get_cleandeal_session_by_id(
    session_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = CleanDealService(db)
    session = await service.get_session_by_id(session_id)
    return APIResponse(success=True, message="Clean deal session fetched successfully", data=session)


@router.get("/cleandeal-sessions/{user_id}", response_model=APIResponse[PaginatedCleanDealSessionRes])
async def get_cleandeal_sessions_by_user(
    user_id: str,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = CleanDealService(db)
    result = await service.get_sessions_by_user(user_id, page, limit)
    return APIResponse(success=True, message="Clean deal sessions fetched successfully", data=result)
