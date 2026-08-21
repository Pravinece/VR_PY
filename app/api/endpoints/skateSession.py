from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.db import mongodb
from app.core.security import get_current_user
from app.schema.skateSessionSchema import CreateSkateSessionReq, SkateSessionRes, PaginatedSkateSessionRes
from app.schema.userSchema import APIResponse
from app.services.skateSessionService import SkateSessionService

router = APIRouter()


async def get_db() -> AsyncIOMotorDatabase:
    return await mongodb.get_database()


@router.post("/skate-sessions", response_model=APIResponse[SkateSessionRes])
async def create_skate_session(
    payload: CreateSkateSessionReq,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = SkateSessionService(db)
    session = await service.create_session(payload)
    
    return APIResponse(success=True, message="Skate session created successfully", data=session)


@router.get("/skate-sessions/session/{session_id}", response_model=APIResponse[SkateSessionRes])
async def get_skate_session_by_id(
    session_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = SkateSessionService(db)
    session = await service.get_session_by_id(session_id)
    return APIResponse(success=True, message="Skate session fetched successfully", data=session)


@router.get("/skate-sessions/{user_id}", response_model=APIResponse[PaginatedSkateSessionRes])
async def get_skate_sessions(
    user_id: str,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = SkateSessionService(db)
    result = await service.get_sessions_by_user(user_id, page, limit)
    return APIResponse(success=True, message="Skate sessions fetched successfully", data=result)


