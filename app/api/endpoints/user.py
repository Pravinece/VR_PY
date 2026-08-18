import logging
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.db import mongodb
from app.schema.userSchema import CreateUserReq, CreateUserRes, APIResponse
from app.services.userService import UserService

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_db() -> AsyncIOMotorDatabase:
    return await mongodb.get_database()


@router.post("/users", response_model=APIResponse[CreateUserRes])
async def create_user(payload: CreateUserReq, db: AsyncIOMotorDatabase = Depends(get_db)):
    service = UserService(db)
    user = await service.create_user(payload)
    return APIResponse(success=True, message="User created successfully", data=user)
