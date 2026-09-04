from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.db import mongodb
from app.schema.cleanDealSchema import CreateCleanDealSessionReq, UpdateCleanDealSessionReq, CleanDealSessionRes
from app.schema.userSchema import APIResponse
from app.services.cleanDealService import CleanDealService
from app.core.security import get_current_user

router = APIRouter()


async def get_db() -> AsyncIOMotorDatabase:
    return await mongodb.get_database()


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
